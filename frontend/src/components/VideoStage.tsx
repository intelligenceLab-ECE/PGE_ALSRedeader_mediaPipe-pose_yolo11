import { RefObject } from "react";

export function VideoStage({ videoRef, overlayRef, className = "", objectFit = "cover" }: {
  videoRef: RefObject<HTMLVideoElement>;
  overlayRef?: RefObject<HTMLCanvasElement>;
  className?: string;
  objectFit?: "cover" | "contain";
}) {
  const fitClass = objectFit === "contain" ? "object-contain bg-black" : "object-cover";
  return (
    <div className={`relative overflow-hidden rounded-xl border border-white/10 ${className}`}>
      <video ref={videoRef} autoPlay muted playsInline className={`h-full w-full ${fitClass}`} />
      {overlayRef ? <canvas ref={overlayRef} className="pointer-events-none absolute inset-0 h-full w-full" /> : null}
    </div>
  );
}
