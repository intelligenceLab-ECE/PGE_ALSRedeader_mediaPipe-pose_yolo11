import { useCallback, useEffect, useMemo, useState } from "react";

type CameraState = {
  stream: MediaStream | null;
  error: string | null;
  granted: boolean;
  running: boolean;
  requestOpen: boolean;
};

const BASE_CONSTRAINTS: MediaStreamConstraints = {
  audio: false,
  video: {
    width: { ideal: 640, max: 640 },
    height: { ideal: 480, max: 480 },
    facingMode: "user",
  },
};

const FALLBACK_CONSTRAINTS: MediaStreamConstraints = {
  audio: false,
  video: {
    width: { ideal: 320, max: 320 },
    height: { ideal: 240, max: 240 },
    facingMode: "user",
  },
};

export function useCamera() {
  const [state, setState] = useState<CameraState>({
    stream: null,
    error: null,
    granted: false,
    running: false,
    requestOpen: true,
  });

  const stop = useCallback(() => {
    setState((prev) => {
      prev.stream?.getTracks().forEach((t) => t.stop());
      return { ...prev, stream: null, running: false };
    });
  }, []);

  const start = useCallback(async () => {
    try {
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia(BASE_CONSTRAINTS);
      } catch {
        stream = await navigator.mediaDevices.getUserMedia(FALLBACK_CONSTRAINTS);
      }
      setState({ stream, error: null, granted: true, running: true, requestOpen: false });
    } catch {
      setState((prev) => ({
        ...prev,
        error: "Acces camera refuse ou indisponible.",
        granted: false,
        running: false,
        requestOpen: true,
      }));
    }
  }, []);

  useEffect(() => stop, [stop]);

  const openPermission = useCallback(() => setState((prev) => ({ ...prev, requestOpen: true })), []);
  const closePermission = useCallback(() => setState((prev) => ({ ...prev, requestOpen: false })), []);

  return useMemo(() => ({ ...state, start, stop, openPermission, closePermission }), [state, start, stop, openPermission, closePermission]);
}
