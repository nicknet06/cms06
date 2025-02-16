let map;
let serviceMarkers = {
    hospital: [],
    police: [],
    fire: []
};

// Icon configurations
const icons = {
    hospital: L.icon({
        iconUrl: '/images/hospital-icon.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    }),
    police: L.icon({
        iconUrl: '/images/police-icon.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    }),
    fire: L.icon({
        iconUrl: '/images/fire-icon.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    })
};

document.addEventListener('DOMContentLoaded', function() {
    initMap();
    loadServices();
    setupEventListeners();
});

function initMap() {
    const greeceCenter = [38.2749497, 23.8102717];
    map = L.map('map').setView(greeceCenter, 7);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

function loadServices() {
    fetch('/api/services')
        .then(response => response.json())
        .then(services => {
            services.forEach(service => {
                addServiceMarker(service);
            });
        })
        .catch(error => console.error('Error loading services:', error));
}

function addServiceMarker(service) {
    const marker = L.marker(
        [service.latitude, service.longitude],
        { icon: icons[service.service_type] }
    );

    const popupContent = `
        <div class="service-info">
            <h3>${service.name}</h3>
            <p>Type: ${service.service_type}</p>
            <p>Address: ${service.address}</p>
            <p>Phone: ${service.phone}</p>
        </div>
    `;

    marker.bindPopup(popupContent);
    marker.addTo(map);
    serviceMarkers[service.service_type].push(marker);
}

function setupEventListeners() {
    // Service type checkboxes
    document.getElementById('show-hospitals').addEventListener('change', function(e) {
        toggleMarkers('hospital', e.target.checked);
    });

    document.getElementById('show-police').addEventListener('change', function(e) {
        toggleMarkers('police', e.target.checked);
    });

    document.getElementById('show-fire').addEventListener('change', function(e) {
        toggleMarkers('fire', e.target.checked);
    });
}

function toggleMarkers(type, show) {
    serviceMarkers[type].forEach(marker => {
        if (show) {
            marker.addTo(map);
        } else {
            marker.remove();
        }
    });
}