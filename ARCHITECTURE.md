# Architecture - AI Playground

## Flux

camera navigateur -> canvas offscreen -> JPEG -> POST /api -> JSON -> overlay canvas

## Backend

- backend/main.py: app FastAPI, /health, /api/meta, static frontend + fallback SPA.
- backend/src/web_api.py: API metiers et chargement modeles.
- ASL: reutilise tflite_infer.py, hand_roi.py, labels.py, utils.py (issus du zip).
- Segmentation: MediaPipe Pose + FaceMesh (face points sous-echantillonnes via SEGMENTATION_FACE_STRIDE).

## Frontend

- React + TypeScript + Vite + Tailwind.
- Pages: Home, ASL, Segmentation.
- Hook webcam: permission modal, start/stop, fallback resolution.
- Hook API frame: throttling reseau (8-12 FPS), fetch multipart.

## Robustesse

- Message explicite si modele ASL absent (model_missing).
- Toast si backend indisponible.
- Ecran aide si camera refusee.
- Limite upload frame via API_FRAME_MAX_SIZE.
