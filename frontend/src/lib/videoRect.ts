export type FitMode = "cover" | "contain";

export type VideoRect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export function getVideoRect(stageWidth: number, stageHeight: number, videoWidth: number, videoHeight: number, fit: FitMode): VideoRect {
  if (!stageWidth || !stageHeight || !videoWidth || !videoHeight) {
    return { x: 0, y: 0, width: stageWidth, height: stageHeight };
  }

  const stageRatio = stageWidth / stageHeight;
  const videoRatio = videoWidth / videoHeight;

  if (fit === "contain") {
    if (videoRatio > stageRatio) {
      const width = stageWidth;
      const height = width / videoRatio;
      return { x: 0, y: (stageHeight - height) / 2, width, height };
    }
    const height = stageHeight;
    const width = height * videoRatio;
    return { x: (stageWidth - width) / 2, y: 0, width, height };
  }

  if (videoRatio > stageRatio) {
    const height = stageHeight;
    const width = height * videoRatio;
    return { x: (stageWidth - width) / 2, y: 0, width, height };
  }
  const width = stageWidth;
  const height = width / videoRatio;
  return { x: 0, y: (stageHeight - height) / 2, width, height };
}
