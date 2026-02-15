"""
Wrapper pour l'inférence TFLite avec gestion automatique des formats d'entrée.
"""

import os
import numpy as np
import cv2
from typing import Tuple, Optional, Dict, Any

try:
    import tensorflow as tf
    TFLITE_AVAILABLE = True
except ImportError:
    TFLITE_AVAILABLE = False
    try:
        import tflite_runtime.interpreter as tflite
        TFLITE_AVAILABLE = True
        tf = None
    except ImportError:
        TFLITE_AVAILABLE = False


class TFLiteModel:
    """
    Wrapper pour charger et utiliser un modèle TFLite avec gestion automatique
    des formats d'entrée (shape, type, normalisation).
    """
    
    def __init__(self, model_path: str):
        """
        Args:
            model_path: Chemin vers le fichier .tflite
            
        Raises:
            FileNotFoundError: Si le modèle n'existe pas
            RuntimeError: Si TFLite n'est pas disponible ou si le modèle est invalide
        """
        if not TFLITE_AVAILABLE:
            raise RuntimeError(
                "TFLite n'est pas disponible. Installez tensorflow ou tflite-runtime."
            )
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modèle non trouvé: {model_path}")
        
        # Charge le modèle
        try:
            if tf is not None:
                self.interpreter = tf.lite.Interpreter(model_path=model_path)
            else:
                self.interpreter = tflite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
        except Exception as e:
            raise RuntimeError(f"Erreur lors du chargement du modèle: {e}")
        
        # Récupère les détails d'entrée et de sortie
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Analyse les détails d'entrée
        input_detail = self.input_details[0]
        self.input_shape = input_detail['shape']
        self.input_dtype = input_detail['dtype']
        self.input_name = input_detail['name']
        
        # Détermine la taille d'entrée (ignore la dimension batch)
        if len(self.input_shape) == 4:  # [batch, height, width, channels]
            self.input_height = self.input_shape[1]
            self.input_width = self.input_shape[2]
            self.input_channels = self.input_shape[3]
        elif len(self.input_shape) == 3:  # [height, width, channels]
            self.input_height = self.input_shape[0]
            self.input_width = self.input_shape[1]
            self.input_channels = self.input_shape[2]
        else:
            raise RuntimeError(f"Shape d'entrée non supportée: {self.input_shape}")
        
        # Détermine le type et la normalisation nécessaires
        self.is_uint8 = self.input_dtype == np.uint8
        self.is_float32 = self.input_dtype == np.float32
        
        print(f"[TFLite] Modèle chargé: {model_path}")
        print(f"[TFLite] Input shape: {self.input_shape}")
        print(f"[TFLite] Input dtype: {self.input_dtype}")
        print(f"[TFLite] Input size: {self.input_width}x{self.input_height}")
        print(f"[TFLite] Normalisation: {'uint8 (pas de normalisation)' if self.is_uint8 else 'float32 ([0,1])'}")
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Pré-traite une image pour correspondre aux exigences du modèle.
        
        Args:
            image: Image BGR (OpenCV) de forme (H, W, 3)
            
        Returns:
            Image pré-traitée prête pour l'inférence
        """
        # Convertit en RGB si nécessaire (MediaPipe utilise RGB)
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume BGR depuis OpenCV, convertit en RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # Redimensionne à la taille d'entrée du modèle
        resized = cv2.resize(image_rgb, (self.input_width, self.input_height))
        
        # Ajoute la dimension batch si nécessaire
        if len(self.input_shape) == 4:
            input_data = np.expand_dims(resized, axis=0)
        else:
            input_data = resized
        
        # Convertit le type et normalise selon le modèle
        if self.is_uint8:
            # Modèle quantifié uint8: pas de normalisation
            input_data = input_data.astype(np.uint8)
        elif self.is_float32:
            # Modèle float32: normalise en [0, 1]
            input_data = input_data.astype(np.float32) / 255.0
        else:
            # Autre type: essaie de convertir en float32 et normalise
            input_data = input_data.astype(np.float32) / 255.0
        
        return input_data
    
    def predict(self, image: np.ndarray) -> Tuple[int, float, np.ndarray]:
        """
        Effectue une prédiction sur une image.
        
        Args:
            image: Image BGR (OpenCV) de forme (H, W, 3)
            
        Returns:
            Tuple (class_index, confidence, all_scores):
            - class_index: Index de la classe prédite
            - confidence: Score de confiance (probabilité)
            - all_scores: Tableau de tous les scores
        """
        # Pré-traite l'image
        input_data = self.preprocess(image)
        
        # Définit l'entrée
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        
        # Lance l'inférence
        self.interpreter.invoke()
        
        # Récupère la sortie
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        # Aplatit si nécessaire (gère batch dimension)
        if len(output_data.shape) > 1:
            scores = output_data[0] if output_data.shape[0] == 1 else output_data.flatten()
        else:
            scores = output_data
        
        # Applique softmax si les scores ne sont pas normalisés (optionnel)
        # La plupart des modèles TFLite ont déjà un softmax intégré
        # Si les scores sont négatifs ou > 1, on applique softmax
        if np.any(scores < 0) or np.max(scores) > 1.0:
            exp_scores = np.exp(scores - np.max(scores))  # Pour stabilité numérique
            scores = exp_scores / np.sum(exp_scores)
        
        # Trouve la classe prédite
        class_index = int(np.argmax(scores))
        confidence = float(scores[class_index])
        
        return class_index, confidence, scores
    
    def get_input_size(self) -> Tuple[int, int]:
        """Retourne la taille d'entrée attendue (width, height)."""
        return self.input_width, self.input_height
