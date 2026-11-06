/**
 * Leaflet.js Map Integration for Smart CivicCare
 * Red = High Priority, Orange = Medium Priority, Green = Low Priority
 */

// Custom SVG Pin Generator
function createCustomPin(color, priority) {
  const iconHtml = `
    <div style="
      background-color: ${color};
      width: 28px;
      height: 28px;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px solid #ffffff;
      box-shadow: 0 3px 8px rgba(0,0,0,0.35);
      cursor: pointer;
    ">
      <div style="
        transform: rotate(45deg);
        color: #ffffff;
        font-size: 11px;
        font-weight: bold;
      ">
        ${priority === 'HIGH' ? '!' : (priority === 'MEDIUM' ? '•' : '✓')}
      </div>
    </div>
  `;

  return L.divIcon({
    html: iconHtml,
    className: 'civic-marker-pin',
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    popupAnchor: [0, -28]
  });
}

/**
 * Initializes master interactive complaints map
 */
function initComplaintsMap(elementId, filterParams = {}) {
  const container = document.getElementById(elementId);
  if (!container) return null;

  // Initialize Map
  const map = L.map(elementId).setView([12.9716, 77.5946], 13);

  // OpenStreetMap Layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors | Smart CivicCare'
  }).addTo(map);

  // Layer group for dynamic updates
  const markersLayer = L.layerGroup().addTo(map);

  function loadMarkers() {
    markersLayer.clearLayers();

    const query = new URLSearchParams(filterParams).toString();
    fetch(`/api/complaints/map?${query}`)
      .then(res => res.json())
      .then(data => {
        if (!data.success || !data.markers.length) return;

        const bounds = [];

        data.markers.forEach(item => {
          const pin = createCustomPin(item.marker_color, item.priority);
          const marker = L.marker([item.lat, item.lng], { icon: pin });

          const photoHtml = item.photo
            ? `<img src="/static/${item.photo}" class="map-popup-img" alt="${item.title}" onerror="this.style.display='none';">`
            : `<div class="map-popup-img d-flex align-items-center justify-content-center text-white bg-dark"><i class="bi bi-geo-alt-fill fs-3 text-secondary"></i></div>`;

          const priorityBadgeClass = item.priority === 'HIGH'
            ? 'badge-priority-high'
            : (item.priority === 'MEDIUM' ? 'badge-priority-medium' : 'badge-priority-low');

          const popupContent = `
            <div class="map-popup-card">
              ${photoHtml}
              <div class="map-popup-body">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <span class="badge ${priorityBadgeClass}">${item.priority}</span>
                  <span class="badge bg-light text-dark border">${item.status}</span>
                </div>
                <h6 class="fw-bold text-dark mb-1 text-truncate" title="${item.title}">${item.title}</h6>
                <p class="small text-muted mb-2"><i class="bi bi-geo-alt text-danger me-1"></i>${item.address}</p>
                <div class="d-flex justify-content-between align-items-center">
                  <small class="text-secondary fw-semibold">${item.ticket_id}</small>
                  <a href="/complaint/${item.id}" class="btn btn-sm btn-civic-teal py-0 px-2" style="font-size: 0.75rem;">View Ticket</a>
                </div>
              </div>
            </div>
          `;

          marker.bindPopup(popupContent);
          markersLayer.addLayer(marker);
          bounds.push([item.lat, item.lng]);
        });

        if (bounds.length > 0) {
          map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
        }
      })
      .catch(err => console.error('Map loading error:', err));
  }

  // Add Legend
  const legend = L.control({ position: 'bottomright' });
  legend.onAdd = function () {
    const div = L.DomUtil.create('div', 'p-2 bg-white rounded shadow-sm border small');
    div.innerHTML = `
      <div class="fw-bold mb-1" style="font-size: 0.75rem;">Complaint Priorities</div>
      <div class="d-flex align-items-center mb-1"><span style="width:12px;height:12px;background:#ef4444;border-radius:50%;display:inline-block;margin-right:6px;"></span>High Priority</div>
      <div class="d-flex align-items-center mb-1"><span style="width:12px;height:12px;background:#f59e0b;border-radius:50%;display:inline-block;margin-right:6px;"></span>Medium Priority</div>
      <div class="d-flex align-items-center"><span style="width:12px;height:12px;background:#10b981;border-radius:50%;display:inline-block;margin-right:6px;"></span>Low Priority</div>
    `;
    return div;
  };
  legend.addTo(map);

  loadMarkers();

  return {
    map: map,
    updateFilters: function (newFilters) {
      filterParams = newFilters;
      loadMarkers();
    }
  };
}

/**
 * Interactive Pin Dropper for Citizen Complaint Form
 */
function initLocationPicker(mapElementId, latInputId, lngInputId, addressInputId) {
  const container = document.getElementById(mapElementId);
  if (!container) return;

  const latInput = document.getElementById(latInputId);
  const lngInput = document.getElementById(lngInputId);
  const addressInput = document.getElementById(addressInputId);

  const initLat = parseFloat(latInput.value) || 12.9716;
  const initLng = parseFloat(lngInput.value) || 77.5946;

  const map = L.map(mapElementId).setView([initLat, initLng], 14);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  // Draggable Pin
  const pin = createCustomPin('#0d9488', 'MEDIUM');
  const marker = L.marker([initLat, initLng], {
    draggable: true,
    icon: pin
  }).addTo(map);

  function updateInputs(lat, lng) {
    latInput.value = lat.toFixed(6);
    lngInput.value = lng.toFixed(6);

    // Trigger AI pre-analysis check whenever location changes significantly
    if (window.triggerAIAnalysis) {
      window.triggerAIAnalysis();
    }
  }

  marker.on('dragend', function (e) {
    const pos = marker.getLatLng();
    updateInputs(pos.lat, pos.lng);
  });

  map.on('click', function (e) {
    marker.setLatLng(e.latlng);
    updateInputs(e.latlng.lat, e.latlng.lng);
  });

  // Locate me button handler if present
  const locateBtn = document.getElementById('btnLocateMe');
  if (locateBtn && navigator.geolocation) {
    locateBtn.addEventListener('click', function () {
      locateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Locating...';
      navigator.geolocation.getCurrentPosition(
        function (pos) {
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;
          map.setView([lat, lng], 16);
          marker.setLatLng([lat, lng]);
          updateInputs(lat, lng);
          locateBtn.innerHTML = '<i class="bi bi-crosshair me-1"></i>Location Acquired!';
          setTimeout(() => {
            locateBtn.innerHTML = '<i class="bi bi-crosshair me-1"></i>Detect My GPS Location';
          }, 3000);
        },
        function (err) {
          alert('GPS location permission denied or unavailable. You can click on the map directly to drop the pin.');
          locateBtn.innerHTML = '<i class="bi bi-crosshair me-1"></i>Detect My GPS Location';
        }
      );
    });
  }

  // Force Leaflet recalculation once visible
  setTimeout(() => map.invalidateSize(), 300);
}

/**
 * Single detail map
 */
function initSingleComplaintMap(elementId, lat, lng, priority, title) {
  const container = document.getElementById(elementId);
  if (!container) return;

  const map = L.map(elementId, { zoomControl: false }).setView([lat, lng], 15);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

  const colorMap = { 'HIGH': '#ef4444', 'MEDIUM': '#f59e0b', 'LOW': '#10b981' };
  const pin = createCustomPin(colorMap[priority] || '#0d9488', priority);
  const marker = L.marker([lat, lng], { icon: pin }).addTo(map);
  marker.bindPopup(`<strong>${title}</strong><br>Coordinates: ${lat.toFixed(4)}, ${lng.toFixed(4)}`).openPopup();
}

