"""
Application principale pour la reconnaissance ASL en temps réel.
"""

import os
import sys
import cv2
import argparse

# Ajoute le répertoire src au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tflite_infer import TFLiteModel
from hand_roi import HandROIExtractor
from labels import load_labels, get_label
from utils import FPSCounter, PredictionSmoother, draw_text_with_background


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Reconnaissance ASL en temps réel avec webcam"
    )
    parser.add_argument(
        '--model',
        type=str,
        default='assets/model.tflite',
        help='Chemin vers le modèle TFLite (défaut: assets/model.tflite)'
    )
    parser.add_argument(
        '--labels',
        type=str,
        default='assets/labels.txt',
        help='Chemin vers le fichier de labels (optionnel, défaut: assets/labels.txt)'
    )
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Index de la webcam (défaut: 0)'
    )
    parser.add_argument(
        '--smoothing',
        type=int,
        default=5,
        help='Taille de la fenêtre de lissage (défaut: 5)'
    )
    parser.add_argument(
        '--padding',
        type=float,
        default=0.2,
        help='Ratio de padding autour de la main (défaut: 0.2)'
    )
    
    args = parser.parse_args()
    
    # Vérifie que le modèle existe
    if not os.path.exists(args.model):
        print(f"ERREUR: Modèle non trouvé: {args.model}")
        print("\nPour télécharger le modèle:")
        print("1. Allez sur https://www.kaggle.com/models/sayannath235/american-sign-language/tfLite/american-sign-language/1")
        print("2. Téléchargez le fichier .tflite")
        print(f"3. Placez-le dans: {args.model}")
        sys.exit(1)
    
    # Charge les labels
    labels = load_labels(args.labels if os.path.exists(args.labels) else None)
    num_classes = len(labels)
    print(f"[App] {num_classes} classes chargées")
    
    # Initialise le modèle TFLite
    try:
        model = TFLiteModel(args.model)
    except Exception as e:
        print(f"ERREUR lors du chargement du modèle: {e}")
        sys.exit(1)
    
    # Initialise l'extracteur de ROI
    roi_extractor = HandROIExtractor(padding_ratio=args.padding)
    
    # Initialise le lisseur de prédictions
    smoother = PredictionSmoother(window_size=args.smoothing)
    
    # Initialise le compteur FPS
    fps_counter = FPSCounter()
    
    # Ouvre la webcam
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"ERREUR: Impossible d'ouvrir la webcam {args.camera}")
        print("Vérifiez que votre webcam est connectée et non utilisée par une autre application.")
        sys.exit(1)
    
    # Configure la résolution de la webcam (optionnel, pour de meilleures performances)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\n[App] Application démarrée!")
    print("[App] Appuyez sur 'q' pour quitter")
    print("[App] Montrez votre main à la caméra pour commencer la reconnaissance\n")
    
    current_label = "No hand"
    current_confidence = 0.0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERREUR: Impossible de lire la frame de la webcam")
                break
            
            # Extrait la ROI de la main
            roi, bbox = roi_extractor.extract_roi(frame)
            
            if roi is not None and bbox is not None:
                # Effectue la prédiction
                try:
                    class_idx, confidence, all_scores = model.predict(roi)
                    
                    # Ajoute la prédiction au lisseur
                    smoother.add_prediction(class_idx, confidence)
                    
                    # Récupère la prédiction lissée
                    smoothed_idx, smoothed_conf = smoother.get_smoothed_prediction()
                    
                    if smoothed_idx is not None:
                        current_label = get_label(smoothed_idx, labels)
                        current_confidence = smoothed_conf
                    else:
                        current_label = "No hand"
                        current_confidence = 0.0
                        
                except Exception as e:
                    print(f"ERREUR lors de la prédiction: {e}")
                    current_label = "Error"
                    current_confidence = 0.0
                
                # Dessine les landmarks et le bounding box
                roi_extractor.draw_landmarks(frame, bbox)
            else:
                # Pas de main détectée
                smoother.reset()
                current_label = "No hand"
                current_confidence = 0.0
            
            # Calcule le FPS
            fps = fps_counter.update()
            
            # Affiche les informations sur la frame
            info_text = f"Label: {current_label}"
            conf_text = f"Confidence: {current_confidence:.2f}"
            fps_text = f"FPS: {fps:.1f}"
            
            # Dessine les textes avec fond
            draw_text_with_background(frame, info_text, (10, 30))
            draw_text_with_background(frame, conf_text, (10, 60))
            draw_text_with_background(frame, fps_text, (10, 90))
            
            # Affiche la frame
            cv2.imshow('ASL Recognition', frame)
            
            # Vérifie si l'utilisateur appuie sur 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n[App] Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n[App] Erreur: {e}")
    finally:
        # Nettoie les ressources
        cap.release()
        cv2.destroyAllWindows()
        roi_extractor.release()
        print("[App] Application fermée")


if __name__ == '__main__':
    main()
