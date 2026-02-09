# Reconnaissance ASL en Temps Réel

Application Python pour reconnaître l'alphabet ASL (American Sign Language) en temps réel à partir d'une webcam, utilisant un modèle TFLite de Kaggle et MediaPipe pour la détection des mains.

## 📋 Prérequis

- Python 3.8 ou supérieur
- Webcam fonctionnelle
- Connexion Internet (pour télécharger le modèle depuis Kaggle)

## 🚀 Installation

### 1. Cloner ou télécharger le projet

```bash
cd ASL_Recognition_App-main
```

### 2. Créer un environnement virtuel (recommandé)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 📥 Téléchargement du Modèle

Le modèle TFLite n'est **pas inclus** dans ce projet. Vous devez le télécharger manuellement depuis Kaggle :

### Étapes pour télécharger le modèle :

1. **Créez un compte Kaggle** (si vous n'en avez pas) : https://www.kaggle.com/

2. **Accédez à la page du modèle** :
   - URL: https://www.kaggle.com/models/sayannath235/american-sign-language/tfLite/american-sign-language/1
   - Ou recherchez "american-sign-language" dans les modèles Kaggle

3. **Téléchargez le fichier .tflite** :
   - Cliquez sur "Download" ou "Download Model"
   - Le fichier téléchargé devrait s'appeler quelque chose comme `model.tflite` ou `american-sign-language.tflite`

4. **Placez le fichier dans le projet** :
   - Renommez-le en `model.tflite` (si nécessaire)
   - Placez-le dans le dossier `assets/` :
     ```
     ASL_Recognition_App-main/
     ├── assets/
     │   └── model.tflite  ← Placez le fichier ici
     ├── src/
     ├── requirements.txt
     └── README.md
     ```

5. **Vérifiez que le fichier existe** :
   ```bash
   # Windows
   dir assets\model.tflite
   
   # macOS/Linux
   ls assets/model.tflite
   ```

### Alternative : Labels personnalisés (optionnel)

Si vous souhaitez utiliser des labels personnalisés, créez un fichier `assets/labels.txt` avec une étiquette par ligne :

```
A
B
C
...
Z
SPACE
DELETE
NOTHING
```

Par défaut, l'application utilise 29 classes ASL standard (A-Z + SPACE + DELETE + NOTHING).

## 🎮 Utilisation

### Lancement de base

```bash
python src/app.py
```

### Options de ligne de commande

```bash
python src/app.py [OPTIONS]
```

**Options disponibles :**

- `--model PATH` : Chemin vers le modèle TFLite (défaut: `assets/model.tflite`)
- `--labels PATH` : Chemin vers le fichier de labels (défaut: `assets/labels.txt`)
- `--camera INDEX` : Index de la webcam à utiliser (défaut: 0)
- `--smoothing N` : Taille de la fenêtre de lissage (défaut: 5)
- `--padding RATIO` : Ratio de padding autour de la main (défaut: 0.2)

**Exemples :**

```bash
# Utiliser une webcam différente (index 1)
python src/app.py --camera 1

# Augmenter le lissage pour des prédictions plus stables
python src/app.py --smoothing 10

# Utiliser un modèle personnalisé
python src/app.py --model path/to/custom_model.tflite
```

### Contrôles

- **'q'** : Quitter l'application
- **Main devant la caméra** : La reconnaissance démarre automatiquement

## 🔧 Dépannage

### Problème : "Modèle non trouvé"

**Symptôme :**
```
ERREUR: Modèle non trouvé: assets/model.tflite
```

**Solutions :**
1. Vérifiez que le fichier `model.tflite` existe dans le dossier `assets/`
2. Vérifiez le chemin avec `--model` si vous avez placé le modèle ailleurs
3. Assurez-vous d'avoir téléchargé le modèle depuis Kaggle (voir section "Téléchargement du Modèle")

### Problème : "Impossible d'ouvrir la webcam"

**Symptôme :**
```
ERREUR: Impossible d'ouvrir la webcam 0
```

**Solutions :**
1. Vérifiez que votre webcam est connectée et fonctionne
2. Fermez les autres applications qui utilisent la webcam (Zoom, Teams, etc.)
3. Essayez un autre index de caméra : `python src/app.py --camera 1`
4. Sur Linux, vérifiez les permissions : `sudo chmod 666 /dev/video0`

### Problème : "TFLite n'est pas disponible"

**Symptôme :**
```
RuntimeError: TFLite n'est pas disponible. Installez tensorflow ou tflite-runtime.
```

**Solutions :**
1. Réinstallez les dépendances : `pip install -r requirements.txt`
2. Vérifiez que TensorFlow est installé : `pip show tensorflow`
3. Si TensorFlow est trop lourd, installez `tflite-runtime` à la place :
   ```bash
   pip install tflite-runtime
   ```

### Problème : "Erreur lors du chargement du modèle"

**Symptôme :**
```
RuntimeError: Erreur lors du chargement du modèle: ...
```

**Solutions :**
1. Vérifiez que le fichier `.tflite` n'est pas corrompu (retéléchargez-le)
2. Vérifiez que vous avez téléchargé le bon modèle (format TFLite, pas un autre format)
3. Vérifiez les permissions du fichier

### Problème : Prédictions instables ou erronées

**Solutions :**
1. Augmentez le lissage : `python src/app.py --smoothing 10`
2. Assurez-vous que la main est bien éclairée
3. Assurez-vous que la main remplit une bonne partie de l'image
4. Réduisez le padding si la ROI est trop grande : `python src/app.py --padding 0.1`

### Problème : Performance faible (FPS bas)

**Solutions :**
1. Réduisez la résolution de la webcam dans le code (modifiez `cap.set()` dans `app.py`)
2. Réduisez la taille de la fenêtre de lissage
3. Fermez les autres applications qui utilisent le CPU/GPU

### Problème : Dépendances manquantes

**Symptôme :**
```
ModuleNotFoundError: No module named 'cv2'
```

**Solutions :**
1. Réinstallez les dépendances : `pip install -r requirements.txt`
2. Vérifiez que vous êtes dans le bon environnement virtuel
3. Sur certains systèmes, OpenCV peut nécessiter : `pip install opencv-python-headless`

## 📁 Structure du Projet

```
ASL_Recognition_App-main/
├── assets/
│   ├── model.tflite          # Modèle TFLite (à télécharger)
│   └── labels.txt            # Labels personnalisés (optionnel)
├── src/
│   ├── app.py                # Application principale
│   ├── tflite_infer.py       # Wrapper TFLite avec gestion adaptative
│   ├── hand_roi.py          # Détection main + extraction ROI
│   ├── labels.py            # Gestion des labels
│   └── utils.py             # Utilitaires (FPS, lissage, affichage)
├── requirements.txt          # Dépendances Python
└── README.md                # Ce fichier
```

## 🎯 Fonctionnalités

- ✅ Détection de la main en temps réel avec MediaPipe Hands
- ✅ Extraction automatique de la ROI (Region of Interest) avec padding configurable
- ✅ Inférence TFLite avec gestion automatique des formats (uint8/float32, normalisation)
- ✅ Lissage temporel des prédictions (majority vote) pour réduire le jitter
- ✅ Affichage en temps réel : label, score de confiance, FPS, ROI
- ✅ Support de 29 classes ASL (A-Z + SPACE + DELETE + NOTHING)
- ✅ Gestion d'erreurs robuste (modèle absent, webcam indisponible, etc.)
- ✅ Compatible Windows/macOS/Linux
- ✅ Fonctionne sur CPU (pas besoin de GPU)

## 🔬 Détails Techniques

### Pré-traitement adaptatif

Le code détecte automatiquement les caractéristiques du modèle TFLite :
- **Taille d'entrée** : Lit dynamiquement depuis `get_input_details()`
- **Type de données** : Supporte `uint8` (quantifié) et `float32`
- **Normalisation** :
  - `uint8` : Pas de normalisation (les valeurs sont déjà en [0, 255])
  - `float32` : Normalisation en [0, 1] (division par 255.0)

### Lissage des prédictions

Utilise un **majority vote** sur les N dernières prédictions (défaut: 5) pour réduire le jitter et améliorer la stabilité.

### Détection de la main

- Utilise MediaPipe Hands pour détecter une seule main
- Calcule un bounding box serré autour des landmarks
- Ajoute un padding configurable (défaut: 20%)
- Affiche les landmarks et le bounding box sur la vidéo

## 📝 Notes

- Le modèle doit être téléchargé manuellement depuis Kaggle (pas d'API incluse)
- L'application fonctionne entièrement en local, aucune connexion cloud requise
- Compatible avec les modèles TFLite standard (input: image RGB, output: logits ou probabilités)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est fourni tel quel pour un usage éducatif et de recherche.
