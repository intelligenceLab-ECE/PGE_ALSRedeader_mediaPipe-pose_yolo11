export type Point = { x: number; y: number };

export type AslResponse = {
  label: string;
  confidence: number;
  fps: number;
  lettersPerSecond: number;
  handLandmarks: Point[];
  bbox: [number, number, number, number] | null;
  modelStatus: string;
  message?: string;
};

export type SegmentationResponse = {
  posePoints: Point[];
  facePoints: Point[];
  modelStatus: string;
  message?: string;
};
