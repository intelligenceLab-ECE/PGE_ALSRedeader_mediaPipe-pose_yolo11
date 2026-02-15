import { MutableRefObject, useEffect, useRef, useState } from "react";

export function useFrameApi<T>(
  videoRef: MutableRefObject<HTMLVideoElement | null>,
  endpoint: string,
  running: boolean,
  fps = 10,
  extraForm?: () => Record<string, string>
) {
  const [result, setResult] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inFlight = useRef(false);

  useEffect(() => {
    if (!running) return;
    const video = videoRef.current;
    if (!video) return;

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) return;

    const interval = Math.max(80, Math.floor(1000 / fps));
    const timer = window.setInterval(async () => {
      if (inFlight.current || !video.videoWidth || !video.videoHeight) return;
      inFlight.current = true;
      try {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.75));
        if (!blob) throw new Error("Capture impossible");

        const formData = new FormData();
        formData.append("frame", blob, "frame.jpg");
        if (extraForm) {
          const extras = extraForm();
          Object.keys(extras).forEach((key) => formData.append(key, extras[key]));
        }

        const response = await fetch(endpoint, { method: "POST", body: formData });
        if (!response.ok) throw new Error(`Erreur API ${response.status}`);
        const payload = (await response.json()) as T;
        setResult(payload);
        setError(null);
      } catch {
        setError("Serveur indisponible");
      } finally {
        inFlight.current = false;
      }
    }, interval);

    return () => window.clearInterval(timer);
  }, [videoRef, endpoint, running, fps, extraForm]);

  return { result, error };
}
