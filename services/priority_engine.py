"""
Smart Priority and Public Safety Engine for Smart CivicCare 2.0.

Calculates explainable Priority Score (0 to 100) and SLA Escalation Guidance:
- HIGH (Score >= 65): Immediate public bodily threat / lethal hazard. SLA: 4 Hours.
- MEDIUM (35 <= Score < 65): Severe civic disruption / moderate hazard. SLA: 24 Hours.
- LOW (Score < 35): Preventative / scheduled cosmetic servicing. SLA: 72 Hours.

Includes immediate escalation guidance for exposed electrical wires and open manholes.
"""

import re

CRITICAL_HAZARDS = [
    (r'(open manhole|missing manhole|uncovered manhole|ಮ್ಯಾನ್‌ಹೋಲ್|मैनहोल|खुला मैनहोल)', 50, "Open sewer manhole poses fatal pedestrian falling hazard"),
    (r'(live wire|exposed wire|electric spark|sparking|electrocution|ವಿದ್ಯುತ್ ತಂತಿ|बिजली का तार|करंट|खुला तार)', 55, "CRITICAL: Exposed live electrical wire poses lethal electrocution threat! Immediate power cutoff required"),
    (r'(sinkhole|cave in|collapsed road|bridge collapse|धंस गई|पुल गिर गया)', 45, "Structural road collapse risk"),
    (r'(deep pothole|crater|major pothole|two wheeler skid|fatal accident|ಗುಂಡಿ|बड़ा गड्ढा|गड्ढे|दुर्घटना)', 40, "Deep crater on fast corridor causing severe vehicular accident danger"),
    (r'(pipeline burst|pipe burst|water gushing|massive flooding|water main burst|ಪೈಪ್ ಒಡೆದು|पाइपलाइन फट|पाइप फटा|पानी बह रहा)', 40, "Major high-pressure potable water main burst flooding roadway"),
    (r'(sewage entering|sewage flooding houses|black water|ಚರಂಡಿ ನೀರು|सीवेज|गटर का पानी)', 40, "Sewage backflow into residential dwellings causing epidemic health emergency"),
    (r'(pole leaning|pole about to fall|falling tree|bent pole|खंभा गिरने)', 35, "Imminent structural fall hazard over roadway"),
    (r'(hospital|emergency|school zone|metro station entrance|fire brigade|अस्पताल|स्कूल)', 30, "Critical emergency hospital / school pedestrian corridor")
]

MEDIUM_HAZARDS = [
    (r'(flickering|complete darkness|dark street|no streetlights|ಕತ್ತಲೆ|अंधेरा|लाइट बंद)', 25, "Pedestrian vulnerability and night-time security hazard"),
    (r'(clogged drain|waterlogged|water stagnancy|mosquito breeding|ನೀರು ನಿಂತಿದೆ|जलभराव|नाली जाम)', 25, "Stagnant drainage and vector-borne epidemic hazard"),
    (r'(overflowing bin|garbage heap|rotting waste|foul smell|ದುರ್ನಾತ|कचरा|कूड़ा|बदबू)', 20, "Sanitary decay and rodent infestation risk"),
    (r'(drinking water leak|clean water waste|seepage|पानी टपक|पानी रिसाव)', 20, "Municipal potable water loss"),
    (r'(broken tiles|cracked sidewalk|footpath broken|फुटपाथ टूटा)', 15, "Pedestrian trip and fall hazard"),
    (r'(damaged divider|broken median|speed breaker damaged|स्पीड ब्रेकर)', 20, "Traffic regulation obstruction")
]

CATEGORY_BASE_HAZARD = {
    'Drainage Problems': 28,
    'Streetlight Failure': 25,
    'Road Damage': 25,
    'Water Leakage': 20,
    'Public Infrastructure Damage': 15,
    'Garbage Collection': 15
}

SEVERITY_WEIGHTS = {
    'Critical': 30,
    'High': 20,
    'Medium': 10,
    'Low': 0,
    'Cosmetic': -10
}

POPULATION_WEIGHTS = {
    '500+ (Entire Ward / Major Hub)': 20,
    '100-500 (Neighborhood / Colony)': 15,
    '50-100 (Street / Crossroad)': 10,
    '10-50 (Local Corridor)': 5,
    '<10 (Individual Property)': 0
}

class SmartPriorityEngine:
    def evaluate(self, title, description, category, severity='Medium', affected_people='10-50'):
        combined = f"{title} {description}".lower()
        score = 0
        detected_triggers = []
        rationales = []
        immediate_escalation_required = False

        # 1. Critical Hazards
        for pattern, pts, desc in CRITICAL_HAZARDS:
            if re.search(pattern, combined, re.IGNORECASE):
                score += pts
                detected_triggers.append(desc)
                rationales.append(f"[+ {pts} pts] {desc}")
                if "live electrical wire" in desc.lower() or "open sewer manhole" in desc.lower():
                    immediate_escalation_required = True

        # 2. Medium Hazards
        for pattern, pts, desc in MEDIUM_HAZARDS:
            if re.search(pattern, combined, re.IGNORECASE):
                score += pts
                detected_triggers.append(desc)
                rationales.append(f"[+ {pts} pts] {desc}")

        # 3. Category Inherent Risk
        base_cat = CATEGORY_BASE_HAZARD.get(category, 15)
        score += base_cat
        rationales.append(f"[+ {base_cat} pts] Inherent hazard baseline for {category}")

        # 4. Reported Severity
        sev_pts = SEVERITY_WEIGHTS.get(severity, 10)
        score += sev_pts
        rationales.append(f"[+ {sev_pts} pts] Reported severity level ({severity})")

        # 5. Affected Radius
        pop_pts = 5
        for k, pts in POPULATION_WEIGHTS.items():
            if str(affected_people).lower() in k.lower():
                pop_pts = pts
                break
        score += pop_pts
        rationales.append(f"[+ {pop_pts} pts] Demographic impact ({affected_people})")

        score = max(5, min(100, score))

        if score >= 65:
            priority = 'HIGH'
            recommended_sla_hours = 4
            hazard_level = 'Critical Public Danger'
        elif score >= 35:
            priority = 'MEDIUM'
            recommended_sla_hours = 24
            hazard_level = 'Significant Civic Disruption'
        else:
            priority = 'LOW'
            recommended_sla_hours = 72
            hazard_level = 'Routine Maintenance'

        explanation = self._build_explanation(priority, score, detected_triggers, category, recommended_sla_hours)

        return {
            'priority': priority,
            'score': score,
            'hazard_level': hazard_level,
            'recommended_sla_hours': recommended_sla_hours,
            'immediate_escalation': immediate_escalation_required,
            'detected_triggers': detected_triggers,
            'rationales': rationales,
            'explanation': explanation
        }

    def _build_explanation(self, priority, score, triggers, category, sla_hours):
        if priority == 'HIGH':
            reason_str = "; ".join(triggers[:2]) if triggers else "acute public bodily threat"
            return (
                f"Classified as HIGH PRIORITY (Safety Risk Score: {score}/100) due to critical safety hazards: {reason_str}. "
                f"Emergency field dispatch initiated under strict {sla_hours}-hour SLA."
            )
        elif priority == 'MEDIUM':
            reason_str = triggers[0] if triggers else f"standard disruption in {category}"
            return (
                f"Assigned MEDIUM PRIORITY (Risk Score: {score}/100) indicating {reason_str}. "
                f"Standard resolution scheduled within {sla_hours} hours."
            )
        else:
            return (
                f"Categorized as LOW PRIORITY (Risk Score: {score}/100). No immediate bodily or structural safety hazards detected. "
                f"Scheduled for routine municipal maintenance within {sla_hours} hours."
            )

priority_engine = SmartPriorityEngine()

def calculate_priority(title, description, category, severity='Medium', affected_people='10-50'):
    return priority_engine.evaluate(title, description, category, severity, affected_people)
