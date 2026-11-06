"""
Train and persist AI complaint classification model.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ai_classifier import AIComplaintClassifier

if __name__ == '__main__':
    print("[AI Training] Initializing and training classifier pipeline...")
    clf = AIComplaintClassifier()
    clf.train_and_save()
    
    # Test sample predictions
    test_cases = [
        "Dangerous open manhole without lid near school gate, deep dark hole",
        "Water supply pipe broke and high pressure water leaking all over the street",
        "Huge pile of uncollected garbage and rotting trash smelling terrible near market",
        "All streetlights dark and dead for 3 nights on the main bypass avenue",
        "Deep pothole and crater on road causing two-wheelers to skid",
        "Broken bench in the public park with splintered wood"
    ]
    
    print("\n[AI Training Verification] Testing on unseen test phrases:")
    for text in test_cases:
        res = clf.predict(text)
        print(f" -> Input: '{text[:45]}...'")
        print(f"    Predicted: {res['category']} (Confidence: {res['confidence_pct']}%, Keywords: {res['keywords_detected']})")

