"""
Gestion des labels pour la reconnaissance ASL.
Fournit un mapping par défaut des 29 classes ASL et permet de charger
des labels personnalisés depuis un fichier.
"""

import os
from pathlib import Path


# Mapping par défaut pour l'alphabet ASL (29 classes)
DEFAULT_LABELS = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'SPACE', 'DELETE', 'NOTHING'
]


def load_labels(labels_path=None):
    """
    Charge les labels depuis un fichier ou retourne les labels par défaut.
    
    Args:
        labels_path: Chemin vers le fichier labels.txt (optionnel)
        
    Returns:
        list: Liste des labels (une par ligne si fichier, sinon DEFAULT_LABELS)
    """
    if labels_path and os.path.exists(labels_path):
        try:
            with open(labels_path, 'r', encoding='utf-8') as f:
                labels = [line.strip() for line in f.readlines() if line.strip()]
            if labels:
                print(f"[Labels] Chargé {len(labels)} labels depuis {labels_path}")
                return labels
            else:
                print(f"[Labels] Fichier vide, utilisation des labels par défaut")
        except Exception as e:
            print(f"[Labels] Erreur lors du chargement de {labels_path}: {e}")
            print(f"[Labels] Utilisation des labels par défaut")
    
    print(f"[Labels] Utilisation des {len(DEFAULT_LABELS)} labels par défaut")
    return DEFAULT_LABELS


def get_label(index, labels=None):
    """
    Retourne le label correspondant à un index.
    
    Args:
        index: Index de la classe
        labels: Liste des labels (optionnel, utilise DEFAULT_LABELS si None)
        
    Returns:
        str: Label correspondant ou "UNKNOWN" si index invalide
    """
    if labels is None:
        labels = DEFAULT_LABELS
    
    if 0 <= index < len(labels):
        return labels[index]
    return "UNKNOWN"
