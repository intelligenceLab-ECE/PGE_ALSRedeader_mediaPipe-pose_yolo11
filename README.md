# AI Playground - Demo educative (ASL + Segmentation)

Application full-stack unique (FastAPI + React/Vite) pour lyceens.

## Fonctionnalites

- ASL recognition (TFLite + ROI main via MediaPipe Hands)
- Segmentation/Pose + Face points (MediaPipe Pose + FaceMesh)
- Webcam navigateur + overlays canvas + controles boutons (sans clavier)
- UI responsive mobile-first
- Frontend build servi par FastAPI (single service Render)

## Variables d'environnement

- ASL_MODEL_PATH (defaut: backend/assets/model.tflite)
- ASL_LABELS_PATH (defaut: backend/assets/labels.txt)
- ASL_MIN_CONFIDENCE (defaut: 0.7)
- API_FRAME_MAX_SIZE (defaut: 921600)
- SEGMENTATION_FACE_STRIDE (defaut: 6)
- optionnel: KAGGLE_USERNAME / KAGGLE_KEY

## Lancer en local (Docker)

```bash
docker build -t ai-playground .
docker run --rm -p 8000:8000 ai-playground
```

## Mode dev

Backend:
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Render free tier

- Deploiement via Dockerfile unique.
- Disque ephemere: poids modeles potentiellement re-telecharges au redemarrage.
- Pour eviter cela: activer Persistent Disk.

### Checklist deploiement Render (ASL + Segmentation)

1) Creer le service
- Render Dashboard -> New -> Web Service
- Connecter le repo duplique
- Environment: `Docker`
- Plan: `Free`

2) Parametres service
- Region: proche de tes utilisateurs
- Auto-Deploy: active (ou desactive si tu preferes manuel)
- Health Check Path: `/health`

3) Variables d'environnement (Render -> Environment)
- `ASL_MODEL_PATH=backend/assets/model.tflite`
- `ASL_LABELS_PATH=backend/assets/labels.txt`
- `API_FRAME_MAX_SIZE=921600`
- `SEGMENTATION_FACE_STRIDE=6`
- Optionnel si telechargement auto du modele: `KAGGLE_USERNAME` et `KAGGLE_KEY`

4) Build/Start
- Rien a changer: le `Dockerfile` racine lance deja `uvicorn backend.main:app`

5) Verification apres deploiement
- Ouvrir `https://<ton-service>.onrender.com/health` -> doit retourner `status: ok`
- Ouvrir la home puis tester:
  - `/asl` (camera + prediction)
  - `/segmentation` (pose + face)

6) Reglages conseilles pour ~5 connexions paralleles
- Garder les FPS faibles (deja configures dans le frontend)
- Ne pas augmenter la resolution camera par defaut
- Si latence: monter `SEGMENTATION_FACE_STRIDE` a `8`

7) Important sur Render Free
- Le service peut "sleep" apres inactivite (premier reveil plus lent)
- Eviter des tests de charge trop longs et continus sur le free tier
