"""
Generates realistic SVG image assets for complaint demonstration in static/uploads.
"""

import os

SVG_TEMPLATES = {
    'pothole_1.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#334155"/>
  <rect x="0" y="190" width="600" height="20" fill="#cbd5e1" stroke-dasharray="30 20"/>
  <!-- Pothole Crater -->
  <ellipse cx="300" cy="240" rx="140" ry="70" fill="#1e293b" stroke="#0f172a" stroke-width="8"/>
  <ellipse cx="290" cy="245" rx="100" ry="45" fill="#020617"/>
  <path d="M 170 230 Q 210 210 260 225 Q 310 205 380 235 Q 430 220 440 250 Q 370 290 280 280 Q 200 290 170 230 Z" fill="#0f172a" opacity="0.6"/>
  <!-- Crack lines -->
  <path d="M 160 230 L 110 210 L 80 240 M 440 250 L 510 260 L 540 230 M 300 310 L 320 370" stroke="#0f172a" stroke-width="4" fill="none"/>
  <!-- Water in pothole -->
  <ellipse cx="280" cy="250" rx="55" ry="20" fill="#38bdf8" opacity="0.7"/>
  <!-- Badge banner -->
  <rect x="20" y="20" rx="8" width="220" height="40" fill="#ef4444" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">CRITICAL ROAD HAZARD</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8">Smart CivicCare Photo Evidence - Ward 12 Main Rd</text>
</svg>''',

    'pothole_fixed.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#334155"/>
  <rect x="0" y="190" width="600" height="20" fill="#cbd5e1" stroke-dasharray="30 20"/>
  <!-- Fresh Asphalt Patch -->
  <ellipse cx="300" cy="240" rx="150" ry="75" fill="#0f172a" stroke="#14b8a6" stroke-width="4"/>
  <ellipse cx="300" cy="240" rx="130" ry="60" fill="#1e293b"/>
  <!-- Roller Marks -->
  <line x1="180" y1="210" x2="420" y2="210" stroke="#334155" stroke-width="2"/>
  <line x1="170" y1="240" x2="430" y2="240" stroke="#334155" stroke-width="2"/>
  <line x1="180" y1="270" x2="420" y2="270" stroke="#334155" stroke-width="2"/>
  <!-- Verified Badge -->
  <rect x="20" y="20" rx="8" width="240" height="40" fill="#10b981" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">REPAIRED &amp; ASPHALTED</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8">Smart CivicCare Resolution Photo - Works Dept</text>
</svg>''',

    'pipe_burst.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#475569"/>
  <!-- Pavement Trench -->
  <rect x="150" y="180" width="300" height="150" fill="#334155" rx="10"/>
  <!-- Cracked Pipeline -->
  <rect x="100" y="230" width="400" height="50" fill="#64748b" rx="6" stroke="#1e293b" stroke-width="3"/>
  <path d="M 280 230 L 320 280 M 310 230 L 290 280" stroke="#ef4444" stroke-width="5"/>
  <!-- Water Spray Geyser -->
  <path d="M 300 230 Q 270 90 250 60 Q 300 130 310 230 Z" fill="#38bdf8" opacity="0.8"/>
  <path d="M 300 230 Q 330 80 360 50 Q 320 120 310 230 Z" fill="#7dd3fc" opacity="0.85"/>
  <!-- Flooding Water Pool -->
  <ellipse cx="300" cy="320" rx="220" ry="50" fill="#0284c7" opacity="0.6"/>
  <!-- Badge -->
  <rect x="20" y="20" rx="8" width="220" height="40" fill="#ef4444" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">MAJOR PIPE BURST</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#cbd5e1">Potable Water Main Seepage - Sector 4</text>
</svg>''',

    'pipe_repaired.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#475569"/>
  <rect x="150" y="180" width="300" height="150" fill="#334155" rx="10"/>
  <!-- Replaced Heavy Duty Pipeline & Coupling Sleeve -->
  <rect x="100" y="230" width="400" height="50" fill="#0284c7" rx="6" stroke="#0369a1" stroke-width="3"/>
  <rect x="260" y="220" width="80" height="70" fill="#0f172a" rx="4" stroke="#e2e8f0" stroke-width="4"/>
  <circle cx="280" cy="235" r="5" fill="#f8fafc"/>
  <circle cx="280" cy="275" r="5" fill="#f8fafc"/>
  <circle cx="320" cy="235" r="5" fill="#f8fafc"/>
  <circle cx="320" cy="275" r="5" fill="#f8fafc"/>
  <!-- Fixed Badge -->
  <rect x="20" y="20" rx="8" width="250" height="40" fill="#10b981" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">REPLACED VALVE SLEEVE</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#cbd5e1">Water Supply &amp; Sewerage Board - SLA Met</text>
</svg>''',

    'garbage_heap.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#f1f5f9"/>
  <!-- Pavement and Wall -->
  <rect x="0" y="0" width="600" height="240" fill="#94a3b8"/>
  <rect x="0" y="240" width="600" height="160" fill="#64748b"/>
  <!-- Overturned Municipal Green Bin -->
  <rect x="80" y="150" width="120" height="140" fill="#15803d" rx="6" stroke="#166534" stroke-width="4"/>
  <circle cx="110" cy="290" r="14" fill="#1e293b"/>
  <circle cx="170" cy="290" r="14" fill="#1e293b"/>
  <!-- Overflowing Trash Heap -->
  <path d="M 160 280 Q 240 160 350 200 Q 420 150 480 230 Q 520 280 490 320 Q 320 340 180 320 Z" fill="#78350f" opacity="0.9"/>
  <circle cx="280" cy="240" r="22" fill="#ca8a04"/>
  <circle cx="340" cy="230" r="28" fill="#eab308"/>
  <circle cx="410" cy="250" r="25" fill="#65a30d"/>
  <rect x="230" y="260" width="45" height="35" fill="#f43f5e" rx="4"/>
  <!-- Flies / Odor squiggles -->
  <path d="M 290 170 Q 300 150 290 140" stroke="#475569" stroke-width="2" fill="none"/>
  <path d="M 360 160 Q 370 140 360 130" stroke="#475569" stroke-width="2" fill="none"/>
  <!-- Badge -->
  <rect x="20" y="20" rx="8" width="250" height="40" fill="#f59e0b" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">ILLEGAL TRASH DUMP</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#ffffff">Market Area Solid Waste - Unattended 4 Days</text>
</svg>''',

    'garbage_cleared.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#f1f5f9"/>
  <rect x="0" y="0" width="600" height="240" fill="#94a3b8"/>
  <rect x="0" y="240" width="600" height="160" fill="#64748b"/>
  <!-- Clean Stainless Municipal Bins neatly arranged -->
  <rect x="180" y="160" width="100" height="120" fill="#15803d" rx="6" stroke="#166534" stroke-width="4"/>
  <rect x="320" y="160" width="100" height="120" fill="#0284c7" rx="6" stroke="#0369a1" stroke-width="4"/>
  <text x="200" y="230" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">WET</text>
  <text x="345" y="230" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">DRY</text>
  <!-- Spotless Footpath with green check -->
  <circle cx="500" cy="200" r="40" fill="#10b981"/>
  <path d="M 485 200 L 495 210 L 515 190" stroke="#ffffff" stroke-width="6" fill="none" stroke-linecap="round"/>
  <!-- Badge -->
  <rect x="20" y="20" rx="8" width="250" height="40" fill="#10b981" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">COMPACTED &amp; SANITIZED</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#ffffff">Solid Waste Management Dept - Resolved</text>
</svg>''',

    'manhole_open.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#334155"/>
  <!-- Sidewalk and Road curb -->
  <rect x="0" y="100" width="600" height="60" fill="#64748b"/>
  <!-- Open Dark Manhole Void -->
  <circle cx="300" cy="260" r="90" fill="#020617" stroke="#dc2626" stroke-width="8"/>
  <circle cx="300" cy="260" r="70" fill="#000000"/>
  <!-- Displaced Iron Lid lying on side -->
  <ellipse cx="440" cy="280" rx="65" ry="40" fill="#475569" stroke="#1e293b" stroke-width="5"/>
  <circle cx="440" cy="280" r="10" fill="#0f172a"/>
  <!-- Warning Barricade tape -->
  <line x1="120" y1="200" x2="480" y2="340" stroke="#fbbf24" stroke-width="8" stroke-dasharray="20 15"/>
  <!-- Badge -->
  <rect x="20" y="20" rx="8" width="280" height="40" fill="#dc2626" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">FATAL HAZARD: OPEN DRAIN</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#cbd5e1">Stormwater Drainage Dept - High Emergency</text>
</svg>''',

    'manhole_covered.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#334155"/>
  <rect x="0" y="100" width="600" height="60" fill="#64748b"/>
  <!-- Brand New Cast Iron Bolted Manhole Cover -->
  <circle cx="300" cy="260" r="90" fill="#1e293b" stroke="#10b981" stroke-width="6"/>
  <circle cx="300" cy="260" r="70" fill="#334155" stroke="#475569" stroke-width="3"/>
  <circle cx="300" cy="260" r="25" fill="#1e293b"/>
  <text x="260" y="265" font-family="Arial, sans-serif" font-weight="bold" font-size="12" fill="#94a3b8">SMART CITY</text>
  <!-- Security Bolts -->
  <circle cx="300" cy="185" r="5" fill="#f8fafc"/>
  <circle cx="375" cy="260" r="5" fill="#f8fafc"/>
  <circle cx="300" cy="335" r="5" fill="#f8fafc"/>
  <circle cx="225" cy="260" r="5" fill="#f8fafc"/>
  <!-- Badge -->
  <rect x="20" y="20" rx="8" width="260" height="40" fill="#10b981" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">REPLACED HEAVY DUTY LID</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#cbd5e1">Drainage Maintenance Team - Verified Safe</text>
</svg>''',

    'streetlight_dark.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#090d16"/>
  <!-- Road Surface -->
  <rect x="0" y="300" width="600" height="100" fill="#1e293b"/>
  <!-- Lamp Pole -->
  <line x1="200" y1="360" x2="200" y2="100" stroke="#475569" stroke-width="12"/>
  <path d="M 200 100 Q 200 60 250 60 L 290 60" stroke="#475569" stroke-width="10" fill="none"/>
  <!-- Broken Lamp head with disconnected wires -->
  <rect x="280" y="50" width="50" height="25" fill="#334155" rx="4"/>
  <path d="M 300 75 Q 310 95 295 110" stroke="#ef4444" stroke-width="3" fill="none"/>
  <path d="M 310 75 Q 330 90 320 105" stroke="#3b82f6" stroke-width="3" fill="none"/>
  <circle cx="305" cy="115" r="6" fill="#f59e0b"/>
  <!-- Badge -->
  <rect x="20" y="20" rx="8" width="270" height="40" fill="#f59e0b" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">STREETLIGHT OUTAGE</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8">Public Lighting Division - Complete Darkness</text>
</svg>''',

    'streetlight_fixed.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#0f172a"/>
  <!-- Glow Halo -->
  <circle cx="305" cy="65" r="160" fill="#38bdf8" opacity="0.15"/>
  <circle cx="305" cy="65" r="90" fill="#fef08a" opacity="0.25"/>
  <!-- Road Surface -->
  <rect x="0" y="300" width="600" height="100" fill="#334155"/>
  <ellipse cx="300" cy="350" rx="220" ry="40" fill="#fef9c3" opacity="0.2"/>
  <!-- Lamp Pole -->
  <line x1="200" y1="360" x2="200" y2="100" stroke="#64748b" stroke-width="12"/>
  <path d="M 200 100 Q 200 60 250 60 L 290 60" stroke="#64748b" stroke-width="10" fill="none"/>
  <!-- Bright LED Luminaire -->
  <rect x="280" y="50" width="55" height="25" fill="#f8fafc" rx="4" stroke="#0284c7" stroke-width="3"/>
  <ellipse cx="307" cy="75" rx="20" ry="10" fill="#fef08a"/>
  <!-- Badge -->
  <rect x="20" y="20" rx="8" width="260" height="40" fill="#10b981" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">NEW SMART LED FITTED</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#cbd5e1">Electrical Division - Lumens Verified</text>
</svg>''',

    'broken_bench.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#ecfdf5"/>
  <!-- Park Lawn and Pathway -->
  <rect x="0" y="200" width="600" height="200" fill="#86efac"/>
  <rect x="0" y="280" width="600" height="120" fill="#d1d5db"/>
  <!-- Broken Park Bench -->
  <rect x="180" y="180" width="16" height="120" fill="#1e293b"/>
  <rect x="380" y="180" width="16" height="120" fill="#1e293b"/>
  <!-- Smashed Wooden Slats -->
  <rect x="160" y="190" width="100" height="15" fill="#92400e" rx="3"/>
  <path d="M 270 195 L 340 230 L 400 190" stroke="#92400e" stroke-width="12" fill="none"/>
  <rect x="160" y="220" width="240" height="15" fill="#78350f" rx="3"/>
  <!-- Splintered wood on ground -->
  <rect x="260" y="295" width="60" height="10" fill="#92400e" transform="rotate(15 260 295)"/>
  <!-- Badge -->
  <rect x="20" y="20" rx="8" width="270" height="40" fill="#0284c7" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">PARK ASSET VANDALISM</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#475569">Public Parks &amp; Infrastructure Dept</text>
</svg>''',

    'bench_repaired.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="100%" height="100%" fill="#ecfdf5"/>
  <rect x="0" y="200" width="600" height="200" fill="#86efac"/>
  <rect x="0" y="280" width="600" height="120" fill="#d1d5db"/>
  <!-- Fully Restored Heavy Duty Park Bench -->
  <rect x="180" y="180" width="16" height="120" fill="#0f172a" rx="4"/>
  <rect x="380" y="180" width="16" height="120" fill="#0f172a" rx="4"/>
  <rect x="160" y="190" width="260" height="15" fill="#15803d" rx="4" stroke="#166534" stroke-width="2"/>
  <rect x="160" y="215" width="260" height="15" fill="#15803d" rx="4" stroke="#166534" stroke-width="2"/>
  <rect x="160" y="240" width="260" height="15" fill="#15803d" rx="4" stroke="#166534" stroke-width="2"/>
  <!-- Badge -->
  <rect x="20" y="20" rx="8" width="250" height="40" fill="#10b981" opacity="0.95"/>
  <text x="35" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffffff">BENCH RESTORED</text>
  <text x="20" y="380" font-family="Arial, sans-serif" font-size="14" fill="#475569">Parks &amp; Amenities Maintenance - Complete</text>
</svg>'''
}

def generate_all_assets():
    target_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    os.makedirs(target_dir, exist_ok=True)
    
    for filename, content in SVG_TEMPLATES.items():
        filepath = os.path.join(target_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated asset: {filename}")

if __name__ == '__main__':
    generate_all_assets()

