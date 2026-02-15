"""
Utilitaires pour le traitement vidéo et le lissage des prédictions.
"""

import time
import collections
from typing import List, Tuple, Optional


class FPSCounter:
    """Compteur de FPS simple."""
    
    def __init__(self, window_size=30):
        """
        Args:
            window_size: Nombre de frames pour calculer la moyenne FPS
        """
        self.window_size = window_size
        self.frame_times = collections.deque(maxlen=window_size)
        self.last_time = time.time()
    
    def update(self):
        """Met à jour le compteur et retourne le FPS actuel."""
        current_time = time.time()
        elapsed = current_time - self.last_time
        self.frame_times.append(elapsed)
        self.last_time = current_time
        
        if len(self.frame_times) > 0:
            avg_time = sum(self.frame_times) / len(self.frame_times)
            fps = 1.0 / avg_time if avg_time > 0 else 0.0
            return fps
        return 0.0


class PredictionSmoother:
    """
    Lisse les prédictions pour réduire le jitter.
    Utilise un majority vote sur les N dernières prédictions.
    """
    
    def __init__(self, window_size=5):
        """
        Args:
            window_size: Nombre de prédictions à considérer pour le vote majoritaire
        """
        self.window_size = window_size
        self.predictions = collections.deque(maxlen=window_size)
    
    def add_prediction(self, class_index: int, confidence: float):
        """
        Ajoute une nouvelle prédiction.
        
        Args:
            class_index: Index de la classe prédite
            confidence: Score de confiance
        """
        self.predictions.append((class_index, confidence))
    
    def get_smoothed_prediction(self) -> Tuple[Optional[int], float]:
        """
        Retourne la prédiction lissée (majority vote).
        
        Returns:
            Tuple (class_index, confidence) ou (None, 0.0) si aucune prédiction
        """
        if not self.predictions:
            return None, 0.0
        
        # Compte les occurrences de chaque classe
        class_counts = {}
        class_confidences = {}
        
        for class_idx, conf in self.predictions:
            if class_idx not in class_counts:
                class_counts[class_idx] = 0
                class_confidences[class_idx] = []
            class_counts[class_idx] += 1
            class_confidences[class_idx].append(conf)
        
        # Trouve la classe la plus fréquente
        if not class_counts:
            return None, 0.0
        
        most_common_class = max(class_counts.items(), key=lambda x: x[1])[0]
        avg_confidence = sum(class_confidences[most_common_class]) / len(class_confidences[most_common_class])
        
        return most_common_class, avg_confidence
    
    def reset(self):
        """Réinitialise l'historique des prédictions."""
        self.predictions.clear()


def draw_text_with_background(img, text, position, font_scale=0.7, 
                              thickness=2, bg_color=(0, 0, 0), 
                              text_color=(255, 255, 255), padding=5):
    """
    Dessine du texte avec un fond semi-transparent pour une meilleure lisibilité.
    
    Args:
        img: Image OpenCV
        text: Texte à afficher
        position: Position (x, y) du texte
        font_scale: Échelle de la police
        thickness: Épaisseur du trait
        bg_color: Couleur du fond (BGR)
        text_color: Couleur du texte (BGR)
        padding: Padding autour du texte
    """
    import cv2
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )
    
    x, y = position
    x1 = x - padding
    y1 = y - text_height - padding
    x2 = x + text_width + padding
    y2 = y + baseline + padding
    
    # Dessine le rectangle de fond
    cv2.rectangle(img, (x1, y1), (x2, y2), bg_color, -1)
    
    # Dessine le texte
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness)
