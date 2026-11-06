"""
Duplicate Complaint Detection Engine for Smart CivicCare.

Identifies potential duplicate issues based on:
1. Geospatial distance (Haversine formula in meters)
2. Semantic / Textual similarity (TF-IDF cosine similarity)
3. Category matching
"""

import math
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth in meters.
    """
    try:
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    except (ValueError, TypeError):
        return 999999.0

    R = 6371000  # Radius of earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

class DuplicateDetector:
    """Detects duplicate infrastructure reports against active database records."""

    def __init__(self, distance_threshold_meters=350, similarity_threshold=0.45):
        self.distance_threshold = distance_threshold_meters
        self.similarity_threshold = similarity_threshold

    def find_duplicate(self, new_title, new_description, new_category, new_lat, new_lng, existing_complaints):
        """
        Scan list of existing active complaints and find closest duplicate match.
        
        Args:
            new_title (str): Complaint title
            new_description (str): Complaint description
            new_category (str): Selected category
            new_lat (float): Latitude
            new_lng (float): Longitude
            existing_complaints (list of dict/Row): Candidate complaints from DB
            
        Returns:
            dict: {
                'is_duplicate': bool,
                'duplicate_of_id': int or None,
                'ticket_id': str or None,
                'similarity_pct': int,
                'distance_meters': float,
                'matched_title': str,
                'advisory': str
            }
        """
        if not existing_complaints:
            return {'is_duplicate': False, 'duplicate_of_id': None, 'similarity_pct': 0, 'distance_meters': 0}

        new_text = f"{new_title} {new_description}".strip().lower()
        if not new_text:
            return {'is_duplicate': False, 'duplicate_of_id': None, 'similarity_pct': 0, 'distance_meters': 0}

        best_match = None
        highest_score = 0.0

        for comp in existing_complaints:
            # Skip resolved or rejected complaints older than 30 days if desired, or prioritize active ones
            status = comp['status'] if isinstance(comp, dict) else comp['status']
            if status in ['Resolved', 'Rejected']:
                continue

            comp_id = comp['id']
            ticket_id = comp['ticket_id']
            comp_title = comp['title']
            comp_desc = comp['description'] or ""
            comp_cat = comp['category']
            comp_lat = comp['latitude']
            comp_lng = comp['longitude']

            dist = haversine_distance(new_lat, new_lng, comp_lat, comp_lng)

            # Proximity limit for consideration (within 600m)
            if dist > 600:
                continue

            comp_text = f"{comp_title} {comp_desc}".strip().lower()
            text_sim = self._calculate_similarity(new_text, comp_text)
            cat_match = (comp_cat.lower() == new_category.lower())

            # Keyword overlap score
            new_words = set(re.findall(r'\b[a-z]{4,}\b', new_text))
            comp_words = set(re.findall(r'\b[a-z]{4,}\b', comp_text))
            shared_words = new_words.intersection(comp_words)
            keyword_overlap_score = len(shared_words) / max(1, len(new_words))

            # Proximity factor: 1.0 at 0m, 0.5 at 150m, 0.0 at 600m
            proximity_factor = max(0.0, 1.0 - (dist / 600.0))

            # Composite match: Proximity (40%) + Text/Keyword (35%) + Category (25%)
            composite_score = (proximity_factor * 0.40) + (max(text_sim, keyword_overlap_score) * 0.35) + (0.25 if cat_match else 0.0)

            # Threshold check:
            # If within 150m and same category with at least 1-2 shared core words (or text_sim > 0.15),
            # or if text_sim >= 0.60 within 600m
            is_match = (
                composite_score >= 0.48 or
                (dist <= 150 and cat_match and (len(shared_words) >= 1 or text_sim >= 0.15)) or
                (dist <= 300 and cat_match and text_sim >= 0.30)
            )

            if is_match and composite_score > highest_score:
                highest_score = composite_score
                display_sim = int(round(max(text_sim, keyword_overlap_score) * 100))
                best_match = {
                    'id': comp_id,
                    'ticket_id': ticket_id,
                    'title': comp_title,
                    'similarity_pct': max(display_sim, int(composite_score * 100)),
                    'distance_meters': dist,
                    'category': comp_cat,
                    'composite_score': composite_score
                }

        if best_match:
            return {
                'is_duplicate': True,
                'duplicate_of_id': best_match['id'],
                'ticket_id': best_match['ticket_id'],
                'similarity_pct': best_match['similarity_pct'],
                'distance_meters': best_match['distance_meters'],
                'matched_title': best_match['title'],
                'advisory': f"Potential duplicate of ticket {best_match['ticket_id']} ('{best_match['title']}') reported {best_match['distance_meters']}m away."
            }

        return {
            'is_duplicate': False,
            'duplicate_of_id': None,
            'similarity_pct': 0,
            'distance_meters': 0,
            'matched_title': '',
            'advisory': 'No similar active complaints found in this vicinity.'
        }

    def _calculate_similarity(self, text1, text2):
        """Compute cosine similarity of TF-IDF vectors."""
        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            tfidf = vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return float(sim)
        except Exception:
            # Word overlap jaccard fallback
            s1 = set(text1.split())
            s2 = set(text2.split())
            if not s1 or not s2:
                return 0.0
            return float(len(s1.intersection(s2))) / float(len(s1.union(s2)))

duplicate_detector = DuplicateDetector()

def check_duplicate(new_title, new_description, new_category, new_lat, new_lng, existing_complaints):
    """Convenience helper to check duplicate."""
    return duplicate_detector.find_duplicate(
        new_title, new_description, new_category, new_lat, new_lng, existing_complaints
    )

