/**
 * SMART CIVICCARE 2.0 - LIVE GPS LOCATION MODULE
 * Complies with Section 7 Live GPS Location Capture:
 * - navigator.geolocation.getCurrentPosition() with high accuracy.
 * - Captures: Latitude, Longitude, GPS accuracy in meters, Capture timestamp.
 * - Interactive Leaflet confirmation map.
 * - Clear permission-denied / manual confirmation fallback (explicitly labeled).
 */

class CivicCareGPS {
  constructor(latInputId, lngInputId, accuracyInputId, manualFlagId) {
    this.latInput = document.getElementById(latInputId);
    this.lngInput = document.getElementById(lngInputId);
    this.accuracyInput = document.getElementById(accuracyInputId);
    this.manualFlag = document.getElementById(manualFlagId);
    this.currentLat = 12.9716;
    this.currentLng = 77.5946;
    this.accuracy = 10.0;
    this.map = null;
    this.marker = null;
  }

  detectLiveLocation() {
    const statusPill = document.getElementById('gpsStatusPill');
    const accuracyBadge = document.getElementById('gpsAccuracyBadge');

    if (!navigator.geolocation) {
      this.handleGPSUnavailable("Geolocation is not supported by your browser environment.");
      return;
    }

    if (statusPill) {
      statusPill.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Acquiring GPS Satellite Signal...';
      statusPill.className = 'badge bg-warning text-dark';
    }

    const options = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    };

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        this.currentLat = pos.coords.latitude;
        this.currentLng = pos.coords.longitude;
        this.accuracy = pos.coords.accuracy || 8.5;

        this.updateInputs(this.currentLat, this.currentLng, this.accuracy, false);

        if (statusPill) {
          statusPill.innerHTML = '<i class="bi bi-geo-alt-fill me-1"></i>Live GPS Verified';
          statusPill.className = 'badge bg-success';
        }
        if (accuracyBadge) {
          accuracyBadge.innerText = `±${Math.round(this.accuracy)}m Accuracy`;
          accuracyBadge.className = 'badge bg-teal bg-opacity-25 text-teal border';
        }

        this.updateMapPosition(this.currentLat, this.currentLng);

        // Notify AI Pre-Triage engine of location update
        if (window.triggerAIAnalysis) {
          window.triggerAIAnalysis();
        }
      },
      (err) => {
        console.warn("GPS acquire error:", err);
        this.handleGPSUnavailable(err.message);
      },
      options
    );
  }

  handleGPSUnavailable(msg) {
    const statusPill = document.getElementById('gpsStatusPill');
    const accuracyBadge = document.getElementById('gpsAccuracyBadge');
    const alertBox = document.getElementById('gpsFallbackAlert');

    if (statusPill) {
      statusPill.innerHTML = '<i class="bi bi-pin-map-fill me-1"></i>Manual Location Confirmed';
      statusPill.className = 'badge bg-secondary';
    }
    if (accuracyBadge) {
      accuracyBadge.innerText = 'Manually Pinned';
      accuracyBadge.className = 'badge bg-light text-muted border';
    }
    if (alertBox) {
      alertBox.classList.remove('d-none');
    }

    this.updateInputs(this.currentLat, this.currentLng, 25.0, true);
  }

  updateInputs(lat, lng, accuracy, isManual) {
    if (this.latInput) this.latInput.value = lat.toFixed(6);
    if (this.lngInput) this.lngInput.value = lng.toFixed(6);
    if (this.accuracyInput) this.accuracyInput.value = accuracy.toFixed(1);
    if (this.manualFlag) this.manualFlag.value = isManual ? '1' : '0';
  }

  initMap(elementId) {
    const container = document.getElementById(elementId);
    if (!container) return;

    this.map = L.map(elementId).setView([this.currentLat, this.currentLng], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(this.map);

    const pinIcon = L.divIcon({
      html: `
        <div style="background-color: #0d9488; width: 28px; height: 28px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); display: flex; align-items: center; justify-content: center; border: 2px solid #ffffff; box-shadow: 0 3px 8px rgba(0,0,0,0.35);">
          <div style="transform: rotate(45deg); color: #ffffff; font-size: 12px; font-weight: bold;"><i class="bi bi-geo-alt-fill"></i></div>
        </div>
      `,
      className: 'gps-marker-pin',
      iconSize: [28, 28],
      iconAnchor: [14, 28]
    });

    this.marker = L.marker([this.currentLat, this.currentLng], {
      draggable: true,
      icon: pinIcon
    }).addTo(this.map);

    this.marker.on('dragend', (e) => {
      const pos = this.marker.getLatLng();
      this.currentLat = pos.lat;
      this.currentLng = pos.lng;
      this.updateInputs(pos.lat, pos.lng, 15.0, true);
      this.handleGPSUnavailable("Pinned manually on map");
    });

    this.map.on('click', (e) => {
      this.marker.setLatLng(e.latlng);
      this.currentLat = e.latlng.lat;
      this.currentLng = e.latlng.lng;
      this.updateInputs(e.latlng.lat, e.latlng.lng, 15.0, true);
      this.handleGPSUnavailable("Pinned manually on map");
    });
  }

  updateMapPosition(lat, lng) {
    if (this.map && this.marker) {
      this.map.setView([lat, lng], 16);
      this.marker.setLatLng([lat, lng]);
    }
  }
}

// Global GPS Instance
window.initCivicGPS = function() {
  window.civicGPS = new CivicCareGPS('inputLat', 'inputLng', 'inputAccuracy', 'isManualLocation');
  window.civicGPS.initMap('gpsConfirmationMap');
  window.civicGPS.detectLiveLocation();
};

