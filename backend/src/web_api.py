"""API web temps reel pour ASL et body points (MediaPipe)."""

from __future__ import annotations

import os
import shutil
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import mediapipe as mp
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from .hand_roi import HandROIExtractor
from .labels import get_label, load_labels
from .tflite_infer import TFLiteModel
from .utils import FPSCounter, PredictionSmoother

try:
    import kagglehub
except Exception:
    kagglehub = None

class AppConfig:
    def __init__(self) -> None:
        self.asl_model_path = os.getenv("ASL_MODEL_PATH", "backend/assets/model.tflite")
        self.asl_labels_path = os.getenv("ASL_LABELS_PATH", "backend/assets/labels.txt")
        self.asl_smoothing = int(os.getenv("ASL_SMOOTHING_WINDOW", "5"))
        self.asl_padding = float(os.getenv("ASL_PADDING", "0.2"))
        self.asl_min_confidence = float(os.getenv("ASL_MIN_CONFIDENCE", "0.7"))
        self.api_frame_max_size = int(os.getenv("API_FRAME_MAX_SIZE", str(900 * 1024)))
        self.segmentation_face_stride = int(os.getenv("SEGMENTATION_FACE_STRIDE", "6"))


CFG = AppConfig()


def _decode_image_bytes(raw: bytes, max_size: int) -> np.ndarray:
    if len(raw) > max_size:
        raise HTTPException(status_code=413, detail=f"Frame too large ({len(raw)} bytes)")
    arr = np.frombuffer(raw, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Image invalide")
    return frame


def _norm_point(x: float, y: float, width: int, height: int) -> Dict[str, float]:
    if width <= 0 or height <= 0:
        return {"x": 0.0, "y": 0.0}
    return {"x": float(max(0.0, min(1.0, x / width))), "y": float(max(0.0, min(1.0, y / height)))}


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _try_download_asl_model(model_path: Path) -> tuple[bool, str]:
    if model_path.exists():
        return True, "model_exists"
    if kagglehub is None:
        return False, "kagglehub_not_available"
    if not (os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY")):
        return False, "kaggle_credentials_missing"
    try:
        _ensure_parent(model_path)
        model_dir = Path(kagglehub.model_download("sayannath235/american-sign-language/tfLite/american-sign-language"))
        candidates = sorted(model_dir.rglob("*.tflite"))
        if not candidates:
            return False, "downloaded_but_no_tflite_found"
        shutil.copy2(candidates[0], model_path)
        return True, "downloaded"
    except Exception as exc:
        return False, f"download_error:{exc}"


class ASLService:
    def __init__(self, cfg: AppConfig) -> None:
        self.lock = threading.Lock()
        self.model_path = Path(cfg.asl_model_path)
        self.labels = load_labels(cfg.asl_labels_path if Path(cfg.asl_labels_path).exists() else None)
        self.roi_extractor = HandROIExtractor(padding_ratio=cfg.asl_padding)
        self.smoother = PredictionSmoother(window_size=cfg.asl_smoothing)
        self.min_confidence = max(0.0, min(1.0, cfg.asl_min_confidence))
        self.fps_counter = FPSCounter()
        self.model: Optional[TFLiteModel] = None
        self.model_status = "initializing"
        self.model_message = ""
        self.current_label = "No hand"
        self.current_confidence = 0.0
        self.last_emit_ts = 0.0
        self.letters_count_current_second = 0
        self.letters_per_second = 0
        self._load_model()

    def _load_model(self) -> None:
        ok, reason = _try_download_asl_model(self.model_path)
        if not ok and not self.model_path.exists():
            self.model_status = "model_missing"
            self.model_message = (
                "ASL model missing. Set ASL_MODEL_PATH or configure KAGGLE_USERNAME/KAGGLE_KEY "
                f"for auto-download. Reason: {reason}"
            )
            return
        try:
            self.model = TFLiteModel(str(self.model_path))
            self.model_status = "loaded"
            self.model_message = "ASL model loaded"
        except Exception as exc:
            self.model_status = "error"
            self.model_message = f"ASL model load error: {exc}"

    def predict(self, frame: np.ndarray) -> Dict[str, Any]:
        with self.lock:
            if self.model is None:
                return {
                    "label": "Model unavailable",
                    "confidence": 0.0,
                    "fps": 0.0,
                    "lettersPerSecond": 0,
                    "handLandmarks": [],
                    "bbox": None,
                    "modelStatus": self.model_status,
                    "message": self.model_message,
                }
            roi, bbox = self.roi_extractor.extract_roi(frame)
            hand_points: List[Dict[str, float]] = []
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.roi_extractor.hands.process(rgb)
            if results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                hand_points = [{"x": float(p.x), "y": float(p.y)} for p in hand.landmark]
            if roi is not None and bbox is not None:
                class_idx, confidence, _ = self.model.predict(roi)
                self.smoother.add_prediction(class_idx, confidence)
                smoothed_idx, smoothed_conf = self.smoother.get_smoothed_prediction()
                if smoothed_idx is not None:
                    if float(smoothed_conf) >= self.min_confidence:
                        self.current_label = get_label(smoothed_idx, self.labels)
                        self.current_confidence = float(smoothed_conf)
                    else:
                        self.current_label = "No hand"
                        self.current_confidence = float(smoothed_conf)
                else:
                    self.current_label = "No hand"
                    self.current_confidence = 0.0
            else:
                self.smoother.reset()
                self.current_label = "No hand"
                self.current_confidence = 0.0
            now = time.time()
            if self.current_label not in ("No hand", "UNKNOWN", "NOTHING", "Error"):
                self.letters_count_current_second += 1
            if now - self.last_emit_ts >= 1.0:
                self.letters_per_second = self.letters_count_current_second
                self.letters_count_current_second = 0
                self.last_emit_ts = now
            fps = float(self.fps_counter.update())
            return {
                "label": self.current_label,
                "confidence": round(self.current_confidence, 4),
                "fps": round(fps, 1),
                "lettersPerSecond": self.letters_per_second,
                "handLandmarks": hand_points,
                "bbox": bbox if bbox is not None else None,
                "modelStatus": self.model_status,
                "message": self.model_message,
            }

    def close(self) -> None:
        with self.lock:
            self.roi_extractor.release()


class SegmentationService:
    def __init__(self, face_stride: int) -> None:
        self.lock = threading.Lock()
        self.model_status = "loaded"
        self.model_message = "MediaPipe Pose + FaceMesh loaded"
        self.face_stride = max(2, min(10, face_stride))
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.mp_face = mp.solutions.face_mesh
        self.face = self.mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def predict(self, frame: np.ndarray, with_face: bool = True) -> Dict[str, Any]:
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with self.lock:
            pose_res = self.pose.process(rgb)
            face_res = self.face.process(rgb) if with_face else None
        pose_points: List[Dict[str, float]] = []
        if pose_res.pose_landmarks:
            pose_points = [_norm_point(lm.x * w, lm.y * h, w, h) for lm in pose_res.pose_landmarks.landmark]
        face_points: List[Dict[str, float]] = []
        if with_face and face_res and face_res.multi_face_landmarks:
            face_landmarks = face_res.multi_face_landmarks[0].landmark
            face_points = [
                _norm_point(lm.x * w, lm.y * h, w, h) for idx, lm in enumerate(face_landmarks) if idx % self.face_stride == 0
            ]
        return {
            "posePoints": pose_points,
            "facePoints": face_points,
            "modelStatus": self.model_status,
            "message": self.model_message,
        }

    def close(self) -> None:
        with self.lock:
            self.pose.close()
            self.face.close()


asl_service = ASLService(CFG)
seg_service = SegmentationService(face_stride=CFG.segmentation_face_stride)

api_router = APIRouter(prefix="/api", tags=["api"])


@api_router.post("/asl/predict")
async def asl_predict(frame: UploadFile = File(...)) -> Dict[str, Any]:
    raw = await frame.read()
    image = _decode_image_bytes(raw, CFG.api_frame_max_size)
    return asl_service.predict(image)


@api_router.post("/segmentation/predict")
async def segmentation_predict(frame: UploadFile = File(...), withFace: str = Form("true")) -> Dict[str, Any]:
    raw = await frame.read()
    image = _decode_image_bytes(raw, CFG.api_frame_max_size)
    with_face = withFace.lower() == "true"
    return seg_service.predict(image, with_face=with_face)


def get_runtime_status() -> Dict[str, Any]:
    return {
        "asl": {"status": asl_service.model_status, "message": asl_service.model_message},
        "mediapipe": {"status": seg_service.model_status, "message": seg_service.model_message},
    }


def get_meta_info() -> Dict[str, Any]:
    return {
        "api": {"name": "AI Playground API", "version": "1.0.0"},
        "models": {
            "asl": {
                "path": str(asl_service.model_path),
                "status": asl_service.model_status,
                "labels": len(asl_service.labels),
            },
            "mediapipe": {
                "pose": "enabled",
                "faceMesh": "enabled",
                "faceDownsample": seg_service.face_stride,
            },
        },
        "config": {"API_FRAME_MAX_SIZE": CFG.api_frame_max_size},
    }


def shutdown_services() -> None:
    asl_service.close()
    seg_service.close()
