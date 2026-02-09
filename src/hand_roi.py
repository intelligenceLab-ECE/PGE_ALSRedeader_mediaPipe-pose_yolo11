"""
Détection de la main avec MediaPipe et extraction de la ROI (Region of Interest).
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Tuple


class HandROIExtractor:
    """
    Extrait la région d'intérêt (ROI) de la main depuis une frame vidéo.
    """
    
    def __init__(self, padding_ratio=0.2, min_detection_confidence=0.5, 
                 min_tracking_confidence=0.5):
        """
        Args:
            padding_ratio: Ratio de padding à ajouter autour du bounding box (0.2 = 20%)
            min_detection_confidence: Confiance minimale pour la détection
            min_tracking_confidence: Confiance minimale pour le tracking
        """
        self.padding_ratio = padding_ratio
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Une seule main pour ASL
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def extract_roi(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]]]:
        """
        Extrait la ROI de la main depuis la frame.
        
        Args:
            frame: Frame BGR depuis OpenCV
            
        Returns:
            Tuple (roi_image, bbox) où:
            - roi_image: Image de la ROI (None si pas de main détectée)
            - bbox: (x_min, y_min, x_max, y_max) en coordonnées de la frame originale
        """
        # Convertit BGR vers RGB pour MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if not results.multi_hand_landmarks:
            return None, None
        
        # Prend la première main détectée
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Calcule le bounding box autour des landmarks
        h, w = frame.shape[:2]
        x_coords = [landmark.x * w for landmark in hand_landmarks.landmark]
        y_coords = [landmark.y * h for landmark in hand_landmarks.landmark]
        
        x_min = int(min(x_coords))
        x_max = int(max(x_coords))
        y_min = int(min(y_coords))
        y_max = int(max(y_coords))
        
        # Ajoute du padding
        width = x_max - x_min
        height = y_max - y_min
        padding_x = int(width * self.padding_ratio)
        padding_y = int(height * self.padding_ratio)
        
        x_min = max(0, x_min - padding_x)
        y_min = max(0, y_min - padding_y)
        x_max = min(w, x_max + padding_x)
        y_max = min(h, y_max + padding_y)
        
        # Extrait la ROI
        roi = frame[y_min:y_max, x_min:x_max]
        
        if roi.size == 0:
            return None, None
        
        return roi, (x_min, y_min, x_max, y_max)
    
    def draw_landmarks(self, frame: np.ndarray, bbox: Optional[Tuple[int, int, int, int]] = None):
        """
        Dessine les landmarks de la main et le bounding box sur la frame.
        
        Args:
            frame: Frame BGR
            bbox: Bounding box (x_min, y_min, x_max, y_max) optionnel
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
        
        # Dessine le bounding box si fourni
        if bbox:
            x_min, y_min, x_max, y_max = bbox
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    
    def release(self):
        """Libère les ressources MediaPipe."""
        self.hands.close()
