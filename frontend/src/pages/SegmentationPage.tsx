import { useEffect, useRef, useState } from "react";

import { ToolTopBar } from "../components/ToolTopBar";
import { VideoStage } from "../components/VideoStage";
import { useCamera } from "../hooks/useCamera";
import { useFrameApi } from "../hooks/useFrameApi";
import { getVideoRect } from "../lib/videoRect";
import { SegmentationResponse } from "../types";
import { Button } from "../ui/button";
import { Dialog } from "../ui/dialog";
import { useToast } from "../ui/toast";

const POSE_CONNECTIONS: Array<[number, number]> = [
  [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8],
  [9, 10], [11, 12], [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
  [17, 19], [12, 14], [14, 16], [16, 18], [16, 20], [16, 22], [18, 20],
  [11, 23], [12, 24], [23, 24], [23, 25], [24, 26], [25, 27], [26, 28],
  [27, 29], [28, 30], [29, 31], [30, 32], [27, 31], [28, 32],
];

export default function SegmentationPage() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const overlayRef = useRef<HTMLCanvasElement | null>(null);
  const camera = useCamera();
  const { pushToast } = useToast();

  const [showPose, setShowPose] = useState(true);
  const [showFace, setShowFace] = useState(true);
  const [showLabels, setShowLabels] = useState(false);

  const { result, error } = useFrameApi<SegmentationResponse>(videoRef, "/api/segmentation/predict", camera.running, 3, () => ({ withFace: String(showFace) }));

  useEffect(() => {
    if (!camera.stream || !videoRef.current) return;
    videoRef.current.srcObject = camera.stream;
  }, [camera.stream]);

  useEffect(() => {
    if (error) pushToast(error);
  }, [error, pushToast]);

  useEffect(() => {
    let raf = 0;
    const draw = () => {
      raf = requestAnimationFrame(draw);
      const canvas = overlayRef.current;
      const video = videoRef.current;
      if (!canvas || !video) return;
      const w = video.clientWidth;
      const h = video.clientHeight;
      if (!w || !h) return;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.fillStyle = "#000";
      ctx.fillRect(0, 0, w, h);
      const rect = getVideoRect(w, h, video.videoWidth, video.videoHeight, "contain");
      if (showPose) {
        const posePoints = result?.posePoints ?? [];
        ctx.strokeStyle = "#16a34a";
        ctx.lineWidth = 2;
        POSE_CONNECTIONS.forEach(([a, b]) => {
          if (!posePoints[a] || !posePoints[b]) return;
          ctx.beginPath();
          ctx.moveTo(rect.x + posePoints[a].x * rect.width, rect.y + posePoints[a].y * rect.height);
          ctx.lineTo(rect.x + posePoints[b].x * rect.width, rect.y + posePoints[b].y * rect.height);
          ctx.stroke();
        });

        ctx.fillStyle = "#22c55e";
        posePoints.forEach((p, idx) => {
          const x = rect.x + p.x * rect.width;
          const y = rect.y + p.y * rect.height;
          ctx.beginPath();
          ctx.arc(x, y, 3, 0, Math.PI * 2);
          ctx.fill();
          if (showLabels) ctx.fillText(String(idx), x + 4, y - 4);
        });
      }
      if (showFace) {
        ctx.fillStyle = "#38bdf8";
        (result?.facePoints ?? []).forEach((p) => {
          ctx.beginPath();
          ctx.arc(rect.x + p.x * rect.width, rect.y + p.y * rect.height, 1.5, 0, Math.PI * 2);
          ctx.fill();
        });
      }
    };
    draw();
    return () => cancelAnimationFrame(raf);
  }, [result, showPose, showFace, showLabels]);

  return (
    <div className="page-shell min-h-screen bg-gradient-to-b from-emerald-950 to-slate-950">
      <Dialog open={camera.requestOpen} title="Autoriser la camera" description="MediaPipe a besoin de la webcam pour detecter le corps et le visage." actions={<Button onClick={() => void camera.start()}>Autoriser</Button>} onClose={camera.closePermission} />
      <ToolTopBar title="Segmentation corps + points + face" controls={<><Button onClick={() => (camera.running ? camera.stop() : void camera.start())}>{camera.running ? "Stop" : "Start"}</Button><Button variant="secondary" onClick={() => setShowPose((v) => !v)}>{showPose ? "Masquer pose" : "Afficher pose"}</Button><Button variant="secondary" onClick={() => setShowFace((v) => !v)}>{showFace ? "Masquer face" : "Afficher face"}</Button><Button variant="outline" onClick={() => setShowLabels((v) => !v)}>{showLabels ? "Masquer labels" : "Afficher labels"}</Button></>} />
      <main className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-3 pb-4">
        <VideoStage videoRef={videoRef} className="aspect-video" objectFit="contain" />
        <div className="relative overflow-hidden rounded-xl border border-white/10"><canvas ref={overlayRef} className="h-full w-full" /></div>
      </main>
    </div>
  );
}
