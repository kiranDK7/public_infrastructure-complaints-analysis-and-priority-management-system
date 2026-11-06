"""
AI Complaint Classification Service for Smart CivicCare 2.0.
Classifies complaints across 6 Municipal Infrastructure Departments:
1. Road Damage (ROADS)
2. Water Leakage (WATER)
3. Garbage Collection (WASTE)
4. Streetlight Failure (LIGHT)
5. Drainage Problems (DRAIN)
6. Public Infrastructure Damage (INFRA)

Supports English and Kannada (ಕನ್ನಡ) smart city keywords with explainability.
"""

import os
import re
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from config import Config

# Curated training corpus with English and bilingual Kannada municipal keywords
TRAINING_DATA = [
    # 1. Road Damage (ROADS)
    ("Deep pothole on main road causing severe traffic jam and vehicle damage", "Road Damage"),
    ("Crater-like pothole near metro pillar 45, two wheelers skidding dangerously", "Road Damage"),
    ("Asphalt road completely eroded and washed away after recent rains", "Road Damage"),
    ("Huge sinkhole opening up in middle of the street, risk of cave in", "Road Damage"),
    ("Tar peeling off, large road cracks and uneven surface causing accidents", "Road Damage"),
    ("Speed breaker damaged and concrete chunks scattered on highway", "Road Damage"),
    ("Road dug up for telecom cable laying and left uncovered for weeks", "Road Damage"),
    ("Broken road divider pieces scattered on fast lane", "Road Damage"),
    ("Severe potholes throughout the entire residential colony main avenue", "Road Damage"),
    ("Unpaved muddy road with severe trenches and ditches making it impassable", "Road Damage"),
    ("Bridge approach road collapsed partially near the flyover ramp", "Road Damage"),
    ("Sharp road depression and subsidence creating dangerous blind bump", "Road Damage"),
    ("Potholes filled with rainwater creating hidden hazards for commuters", "Road Damage"),
    ("Flyover expansion joint broken and steel rods exposed", "Road Damage"),
    ("ರಸ್ತೆಯಲ್ಲಿ ದೊಡ್ಡ ಗುಂಡಿ ಬಿದ್ದಿದೆ ವಾಹನ ಸವಾರರಿಗೆ ಅಪಾಯ gundi pothole road damage", "Road Damage"),
    ("ಡಾಂಬರು ಕಿತ್ತು ಹೋಗಿದೆ ರಸ್ತೆ ಹಾಳಾಗಿದೆ asphalt road peeled off", "Road Damage"),
    ("सड़क पर बहुत बड़ा और गहरा गड्ढा है जिससे गाड़ियां दुर्घटनाग्रस्त हो रही हैं", "Road Damage"),
    ("डामर पूरी तरह उखड़ गया है और सड़क चलने लायक नहीं बची है", "Road Damage"),
    ("फ्लाईओवर के पास सड़क धंस गई है और बड़ा गड्ढा बन गया है", "Road Damage"),

    # 2. Water Leakage (WATER)
    ("Underground municipal drinking water main line burst, clean water gushing onto street", "Water Leakage"),
    ("Major pipeline fracture causing massive water wastage and low pressure in houses", "Water Leakage"),
    ("Drinking water pipe leaking continuously for three days near park corner", "Water Leakage"),
    ("High pressure water fountain erupting from broken underground pipe joint", "Water Leakage"),
    ("Overhead municipal water tank overflowing continuously due to broken float valve", "Water Leakage"),
    ("Water supply contaminated and brown muddy water coming in taps due to pipe breach", "Water Leakage"),
    ("Public drinking water tap broken and water flowing continuously onto footpath", "Water Leakage"),
    ("Underground supply pipe crack leaking thousands of liters per hour", "Water Leakage"),
    ("Severe water shortage in ward 12 because of fractured distribution main", "Water Leakage"),
    ("Fire hydrant valve leaking pressurized water across sidewalk", "Water Leakage"),
    ("ಕುಡಿಯುವ ನೀರಿನ ಪೈಪ್ ಒಡೆದು ನೀರು ಪೋಲಾಗುತ್ತಿದೆ water pipe leakage burst", "Water Leakage"),
    ("ಕೊಳಾಯಿ ನೀರು ಪೂರೈಕೆ ಸ್ಥಗಿತಗೊಂಡಿದೆ water supply pipeline damaged", "Water Leakage"),
    ("पीने के पानी का मुख्य पाइप टूट गया है और भारी मात्रा में पानी बर्बाद हो रहा है", "Water Leakage"),
    ("नल का कनेक्शन टूट गया है और सड़क पर फव्वारे की तरह पानी निकल रहा है", "Water Leakage"),

    # 3. Garbage Collection (WASTE)
    ("Huge heap of uncollected solid waste and rotting garbage near vegetable market", "Garbage Collection"),
    ("Overflowing municipal green dumpster bins not cleared for four days", "Garbage Collection"),
    ("Illegal open dumping of construction debris and plastic waste on sidewalk", "Garbage Collection"),
    ("Stray cattle and dogs scattering open rotting garbage and plastic bags", "Garbage Collection"),
    ("Foul smell and fly infestation from rotting waste dump near residential colony", "Garbage Collection"),
    ("Garbage truck has not visited our street for an entire week", "Garbage Collection"),
    ("Bio-medical waste and chemical containers dumped illegally in public park corner", "Garbage Collection"),
    ("Public dustbin broken and overturned, trash littering the entire footpath", "Garbage Collection"),
    ("Burning of municipal waste and plastic in open plot causing toxic smoke", "Garbage Collection"),
    ("ಕಸ ಸಂಗ್ರಹಣೆ ಸರಿಯಾಗಿ ನಡೆಯುತ್ತಿಲ್ಲ ದುರ್ನಾತ ಬರುತ್ತಿದೆ garbage waste dump uncollected", "Garbage Collection"),
    ("ರಸ್ತೆ ಬದಿಯಲ್ಲಿ ಕಸದ ರಾಶಿ ಬಿದ್ದಿದೆ littering trash heap near market", "Garbage Collection"),
    ("कचरे का बहुत बड़ा ढेर लगा हुआ है जिससे तीव्र दुर्गंध और बीमारियां फैल रही हैं", "Garbage Collection"),
    ("कचरा उठाने वाली गाड़ी कई दिनों से नहीं आई है और डस्टबिन ओवरफ्लो हो गया है", "Garbage Collection"),

    # 4. Streetlight Failure (LIGHT)
    ("All streetlights on main avenue are completely dark for past two nights", "Streetlight Failure"),
    ("Flickering LED street lamp pole causing severe disturbance and vision hazard", "Streetlight Failure"),
    ("Electric pole damaged in storm, hanging low with loose live wires exposed", "Streetlight Failure"),
    ("Streetlight junction box door open with exposed live wires accessible to children", "Streetlight Failure"),
    ("Entire neighborhood plunged into darkness, high risk of theft and accidents", "Streetlight Failure"),
    ("Broken lamp glass fixture hanging precariously from pole above sidewalk", "Streetlight Failure"),
    ("Solar streetlight battery stolen and pole light not functioning", "Streetlight Failure"),
    ("Short circuit sparks coming from street lighting pole transformer", "Streetlight Failure"),
    ("ರಸ್ತೆ ದೀಪಗಳು ಉರಿಯುತ್ತಿಲ್ಲ ಕತ್ತಲೆಯಾಗಿದೆ streetlight dark broken", "Streetlight Failure"),
    ("ವಿದ್ಯುತ್ ತಂತಿ ತೂಗಾಡುತ್ತಿದೆ ಅಪಾಯ live electric wire sparking hazard", "Streetlight Failure"),
    ("स्ट्रीट लाइट खराब है और पूरी सड़क पर रात को गहरा अंधेरा छाया रहता है", "Streetlight Failure"),
    ("बिजली का खंभा झुक गया है और नंगे तार लटक रहे हैं करंट लगने का खतरा है", "Streetlight Failure"),

    # 5. Drainage Problems (DRAIN)
    ("Open manhole cover missing on busy walkway, lethal death trap for pedestrians", "Drainage Problems"),
    ("Severe sewage overflow from choked gutter flooding residential road with dirty water", "Drainage Problems"),
    ("Stormwater drain completely clogged with silt and plastic, street waterlogged", "Drainage Problems"),
    ("Underground sewer line blocked and black filthy water backing up into houses", "Drainage Problems"),
    ("Broken concrete slab over stormwater drain collapsed under car wheel", "Drainage Problems"),
    ("Rainwater drain overflow during normal rain due to lack of pre-monsoon desilting", "Drainage Problems"),
    ("Open gutter without safety grill, risk of small children falling inside", "Drainage Problems"),
    ("Urban waterlogging and flooding on crossroad, vehicles stalled in knee-deep water", "Drainage Problems"),
    ("ಚರಂಡಿ ನೀರು ರಸ್ತೆಯ ಮೇಲೆ ಹರಿಯುತ್ತಿದೆ ಒಳಚರಂಡಿ ಬಂದ್ ಆಗಿದೆ drainage sewage blocked", "Drainage Problems"),
    ("ಮ್ಯಾನ್‌ಹೋಲ್ ಮುಚ್ಚಳ ತೆರೆದಿದೆ ಅಪಾಯಕಾರಿ open manhole cover missing", "Drainage Problems"),
    ("नाली पूरी तरह से जाम हो गई है और सीवेज का गंदा बदबूदार पानी सड़क पर बह रहा है", "Drainage Problems"),
    ("सड़क के बीच खुला मैनहोल बिना ढक्कन के है जिससे जानलेवा दुर्घटना हो सकती है", "Drainage Problems"),
    ("बारिश के कारण सड़क पर भारी जलभराव हो गया है और गाड़ियां डूब रही हैं", "Drainage Problems"),

    # 6. Public Infrastructure Damage (INFRA)
    ("Public bus stop shelter roof collapsed and metal seating bench vandalized", "Public Infrastructure Damage"),
    ("Broken concrete pedestrian footpath tiles and open utility duct traps", "Public Infrastructure Damage"),
    ("Public park children play swing and slide broken with jagged rusty iron edges", "Public Infrastructure Damage"),
    ("Pedestrian foot overbridge railing rusted, detached, and missing safety bars", "Public Infrastructure Damage"),
    ("Public toilet door broken, taps stolen, and facility in dilapidated condition", "Public Infrastructure Damage"),
    ("Crash barrier on flyover curved turn smashed by truck and not repaired", "Public Infrastructure Damage"),
    ("Smart city information kiosk screen smashed and vandalized", "Public Infrastructure Damage"),
    ("ಸಾರ್ವಜನಿಕ ಉದ್ಯಾನವನದ ಆಸನಗಳು ಮುರಿದಿವೆ public park bench broken", "Public Infrastructure Damage"),
    ("ಬಸ್ ನಿಲ್ದಾಣದ ಮೇಲ್ಛಾವಣಿ ಹಾಳಾಗಿದೆ bus shelter roof damaged", "Public Infrastructure Damage"),
    ("सार्वजनिक शौचालय की हालत बहुत खराब है नल चोरी हो गए हैं और दरवाजे टूटे हैं", "Public Infrastructure Damage"),
    ("बस स्टैंड का शेड गिर गया है और बैठने के लिए बेंच टूटी हुई हैं", "Public Infrastructure Damage"),
    ("फुटपाथ की टाइलें और स्लैब टूटे हुए हैं पैदल चलने वालों को चोट लग रही है", "Public Infrastructure Damage")
]

class AIComplaintClassifier:
    """NLP Classifier using TF-IDF and Logistic Regression."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIComplaintClassifier, cls).__new__(cls)
            cls._instance._model = None
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        model_path = Config.ML_MODEL_PATH
        if os.path.exists(model_path):
            try:
                self._model = joblib.load(model_path)
                return
            except Exception as e:
                print(f"[AI Classifier] Loading saved model failed: {e}. Retraining...")
        self.train_and_save()

    def train_and_save(self):
        texts = [item[0] for item in TRAINING_DATA]
        labels = [item[1] for item in TRAINING_DATA]

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),
                lowercase=True,
                max_features=3000,
                sublinear_tf=True
            )),
            ('clf', LogisticRegression(
                C=3.0,
                max_iter=400,
                class_weight='balanced'
            ))
        ])

        pipeline.fit(texts, labels)
        self._model = pipeline

        try:
            os.makedirs(os.path.dirname(Config.ML_MODEL_PATH), exist_ok=True)
            joblib.dump(pipeline, Config.ML_MODEL_PATH)
            print(f"[AI Classifier 2.0] Model successfully saved to {Config.ML_MODEL_PATH}")
        except Exception as e:
            print(f"[AI Classifier 2.0] Model save error: {e}")

    def predict(self, text):
        if not text or not text.strip():
            return {
                'category': 'Public Infrastructure Damage',
                'suggested_department_code': 'INFRA',
                'confidence': 0.5,
                'confidence_pct': 50,
                'all_probabilities': {},
                'keywords_detected': []
            }

        cleaned = self._clean_text(text)
        if self._model is None:
            self._init_model()

        try:
            probs = self._model.predict_proba([cleaned])[0]
            classes = list(self._model.classes_)
            prob_dict = {cls_name: float(prob) for cls_name, prob in zip(classes, probs)}

            # Domain keyword reinforcement boost for high precision smart city triage
            boost_rules = {
                'Drainage Problems': ['manhole', 'sewer', 'sewage', 'gutter', 'drain', 'drainage', 'culvert', 'waterlog', 'flooding', 'ಮ್ಯಾನ್‌ಹೋಲ್', 'ಚರಂಡಿ'],
                'Water Leakage': ['water pipe', 'pipeline', 'pipe burst', 'water leak', 'tap broken', 'drinking water', 'hydrant', 'ನೀರು', 'ಪೈಪ್'],
                'Road Damage': ['pothole', 'sinkhole', 'crater', 'asphalt', 'tar', 'flyover', 'divider', 'speed breaker', 'ಗುಂಡಿ', 'ರಸ್ತೆ'],
                'Garbage Collection': ['garbage', 'dump', 'dumpster', 'trash', 'waste', 'rotting', 'bin', 'stench', 'ಕಸ'],
                'Streetlight Failure': ['streetlight', 'street light', 'lamp', 'darkness', 'blackout', 'light pole', 'sparking', 'live wire', 'ದೀಪ', 'ವಿದ್ಯುತ್'],
                'Public Infrastructure Damage': ['bench', 'bus stop', 'footpath', 'railing', 'play swing', 'kiosk', 'sidewalk', 'ಉದ್ಯಾನವನ', 'ಬಸ್']
            }

            for cat, kws in boost_rules.items():
                match_count = sum(1 for kw in kws if kw.lower() in cleaned)
                if match_count > 0 and cat in prob_dict:
                    prob_dict[cat] += match_count * 0.40

            # Normalize
            total = sum(prob_dict.values())
            for c in prob_dict:
                prob_dict[c] = round(prob_dict[c] / total, 4)

            best_cat = max(prob_dict, key=prob_dict.get)
            best_conf = prob_dict[best_cat]
            keywords = self._extract_keywords(cleaned)

            dept_map = {
                'Road Damage': 'ROADS',
                'Water Leakage': 'WATER',
                'Garbage Collection': 'WASTE',
                'Streetlight Failure': 'LIGHT',
                'Drainage Problems': 'DRAIN',
                'Public Infrastructure Damage': 'INFRA'
            }

            return {
                'category': best_cat,
                'suggested_department_code': dept_map.get(best_cat, 'INFRA'),
                'confidence': round(best_conf, 3),
                'confidence_pct': int(round(best_conf * 100)),
                'all_probabilities': prob_dict,
                'keywords_detected': keywords
            }
        except Exception as e:
            print(f"[AI Classifier] Prediction fallback: {e}")
            return {
                'category': 'Road Damage',
                'suggested_department_code': 'ROADS',
                'confidence': 0.70,
                'confidence_pct': 70,
                'all_probabilities': {},
                'keywords_detected': ['road', 'damage']
            }

    def _clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[\r\n\t]+', ' ', text)
        return text.strip()

    def _extract_keywords(self, text):
        tokens = [
            "pothole", "crater", "sinkhole", "asphalt", "divider", "pipeline", "pipe burst", "leakage",
            "drinking water", "garbage", "waste", "dumpster", "dumping", "streetlight", "blackout",
            "live wire", "sparking", "manhole", "sewer", "sewage", "gutter", "waterlogging", "footpath",
            "bench", "bus stop", "ಗುಂಡಿ", "ನೀರು", "ಕಸ", "ದೀಪ", "ಚರಂಡಿ"
        ]
        return [tok for tok in tokens if tok in text][:6]

classifier = AIComplaintClassifier()

def classify_complaint(text):
    return classifier.predict(text)
