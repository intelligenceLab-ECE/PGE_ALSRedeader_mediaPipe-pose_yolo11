import { useEffect, useMemo, useRef, useState } from "react";

import { ToolTopBar } from "../components/ToolTopBar";
import { VideoStage } from "../components/VideoStage";
import { useCamera } from "../hooks/useCamera";
import { useFrameApi } from "../hooks/useFrameApi";
import { getVideoRect } from "../lib/videoRect";
import { AslResponse } from "../types";
import { Button } from "../ui/button";
import { Dialog } from "../ui/dialog";
import { useToast } from "../ui/toast";
import alphabetImage from "../assets/alphabet.jpg";

const HAND_CONNECTIONS: Array<[number, number]> = [
  [0, 1],[1, 2],[2, 3],[3, 4],[0, 5],[5, 6],[6, 7],[7, 8],[5, 9],[9, 10],[10, 11],[11, 12],[9, 13],[13, 14],[14, 15],[15, 16],[13, 17],[17, 18],[18, 19],[19, 20],[0, 17],
];

export default function AslPage() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const overlayRef = useRef<HTMLCanvasElement | null>(null);
  const [showLandmarks, setShowLandmarks] = useState(true);
  const [freeze, setFreeze] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const camera = useCamera();
  const { pushToast } = useToast();

  const { result, error } = useFrameApi<AslResponse>(videoRef, "/api/asl/predict", camera.running && !freeze, 4);

  useEffect(() => {
    if (!camera.stream || !videoRef.current) return;
    videoRef.current.srcObject = camera.stream;
  }, [camera.stream]);

  useEffect(() => {
    if (error) pushToast(error);
  }, [error, pushToast]);

  useEffect(() => {
    if (!result?.label || ["No hand", "UNKNOWN", "NOTHING"].includes(result.label)) return;
    setHistory((prev) => [result.label, ...prev].slice(0, 50));
  }, [result?.label]);

  useEffect(() => {
    let raf = 0;
    const draw = () => {
      raf = requestAnimationFrame(draw);
      const video = videoRef.current;
      const canvas = overlayRef.current;
      if (!video || !canvas || !result) return;
      const w = video.clientWidth;
      const h = video.clientHeight;
      if (!w || !h) return;
      if (canvas.width != w || canvas.height != h) {
        canvas.width = w;
        canvas.height = h;
      }
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.clearRect(0, 0, w, h);
      if (!showLandmarks) return;
      const rect = getVideoRect(w, h, video.videoWidth, video.videoHeight, "cover");
      const pts = result.handLandmarks || [];
      ctx.lineWidth = 2;
      ctx.strokeStyle = "#22d3ee";
      HAND_CONNECTIONS.forEach(([a, b]) => {
        if (!pts[a] || !pts[b]) return;
        ctx.beginPath();
        ctx.moveTo(rect.x + pts[a].x * rect.width, rect.y + pts[a].y * rect.height);
        ctx.lineTo(rect.x + pts[b].x * rect.width, rect.y + pts[b].y * rect.height);
        ctx.stroke();
      });
      ctx.fillStyle = "#a78bfa";
      pts.forEach((p) => {
        ctx.beginPath();
        ctx.arc(rect.x + p.x * rect.width, rect.y + p.y * rect.height, 3, 0, Math.PI * 2);
        ctx.fill();
      });
    };
    draw();
    return () => cancelAnimationFrame(raf);
  }, [result, showLandmarks]);

  const modelInfo = useMemo(() => {
    if (!result) return "en attente";
    if (result.modelStatus === "loaded") return "modele charge";
    return result.message || "modele indisponible";
  }, [result]);

  return (
    <div className="page-shell min-h-screen bg-gradient-to-b from-indigo-950 to-slate-950">
      <Dialog open={camera.requestOpen} title="Autoriser la camera" description="Cette demo a besoin de la webcam pour envoyer des images vers l'API." actions={<Button onClick={() => void camera.start()}>Autoriser</Button>} onClose={camera.closePermission} />

      <ToolTopBar title="ASL Recognition" controls={<><Button onClick={() => (camera.running ? camera.stop() : void camera.start())}>{camera.running ? "Stop camera" : "Start camera"}</Button><Button variant="secondary" onClick={() => setFreeze((v) => !v)}>{freeze ? "Unfreeze" : "Freeze"}</Button><Button variant="outline" onClick={() => setShowLandmarks((v) => !v)}>{showLandmarks ? "Masquer landmarks" : "Afficher landmarks"}</Button></>} />

      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-3 pb-4">
        <VideoStage videoRef={videoRef} overlayRef={overlayRef} className="aspect-video" />
        <div className="glass flex flex-col gap-2 p-3">
          <div className="flex flex-wrap items-center gap-4">
            <p className="text-xl font-bold text-violet-300">{result?.label ?? "--"}</p>
            <p className="text-sm text-slate-300">Confiance: {Math.round((result?.confidence ?? 0) * 100)}%</p>
            <p className="text-sm text-slate-300">Lettres/sec: {result?.lettersPerSecond ?? 0}</p>
            <p className="text-xs text-slate-400">{modelInfo}</p>
          </div>
          <div className="overflow-x-auto whitespace-nowrap text-sm text-slate-200">{history.length ? history.join("  |  ") : "Historique vide"}</div>
          {camera.error ? <p className="text-sm text-rose-300">{camera.error}</p> : null}
        </div>
        <div className="relative overflow-hidden rounded-xl border border-white/10 bg-black aspect-video">
          <img
            src={alphabetImage}
            alt="Alphabet ASL"
            className="h-full w-full object-contain"
          />
        </div>
      </div>
    </div>
  );
}
