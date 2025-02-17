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
    showLoading();
    fetch('/api/services')
        .then(response => response.json())
        .then(services => {
            services.forEach(service => {
                addServiceMarker(service);
            });
            hideLoading();
        })
        .catch(error => {
            console.error('Error loading services:', error);
            showError('Failed to load emergency services');
            hideLoading();
        });
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
            <button onclick="showServiceResources(${service.id}, '${service.name}', '${service.service_type}')" class="view-resources-btn">View Resources</button>
        </div>
    `;

    marker.bindPopup(popupContent);
    marker.on('click', () => {
        showServiceResources(service.id, service.name, service.service_type);
    });
    marker.addTo(map);
    serviceMarkers[service.service_type].push(marker);
}

async function showServiceResources(serviceId, serviceName, serviceType) {
    const resourcesPanel = document.getElementById('resources-panel');
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '<span class="spinner"></span> Loading resources...';

    // Clear previous content and show loading
    resourcesPanel.innerHTML = '';
    resourcesPanel.appendChild(loadingIndicator);
    resourcesPanel.style.display = 'block';

    try {
        const response = await fetch(`/api/services/${serviceId}/resources`);
        if (!response.ok) {
            throw new Error('Failed to fetch resources');
        }
        const data = await response.json();

        // Update service details with close button
        const serviceDetails = `
            <div class="panel-header">
                <div class="service-header ${serviceType}">
                    <h4>${serviceName}</h4>
                    <span class="service-type">${serviceType}</span>
                </div>
                <button class="close-resources-btn" onclick="closeResourcesPanel()">
                    <span class="close-icon">×</span>
                </button>
            </div>
        `;

        // Create resources content
        const resourcesContent = `
            <div class="service-details">${serviceDetails}</div>
            
            <div class="resource-group">
                <h4>Equipment</h4>
                <div class="resource-items">
                    ${renderEquipmentList(data.equipment)}
                </div>
            </div>

            <div class="resource-group">
                <h4>Vehicles</h4>
                <div class="resource-items">
                    ${renderVehicleList(data.vehicles)}
                </div>
            </div>

            <div class="resource-group">
                <h4>Personnel</h4>
                <div class="resource-items">
                    ${renderPersonnelList(data.personnel)}
                </div>
            </div>
        `;

        resourcesPanel.innerHTML = resourcesContent;
    } catch (error) {
        console.error('Error loading resources:', error);
        resourcesPanel.innerHTML = `
            <div class="error-message">
                Failed to load resources. Please try again later.
                <button onclick="showServiceResources(${serviceId}, '${serviceName}', '${serviceType}')" class="retry-btn">Retry</button>
                <button class="close-resources-btn" onclick="closeResourcesPanel()">
                    <span class="close-icon">×</span>
                </button>
            </div>
        `;
    }
}

// Add this new function to handle closing the panel
function closeResourcesPanel() {
    const resourcesPanel = document.getElementById('resources-panel');
    resourcesPanel.style.display = 'none';
    resourcesPanel.innerHTML = ''; // Clear the content
}
function renderEquipmentList(equipment) {
    if (!equipment || equipment.length === 0) {
        return '<p class="no-data">No equipment available</p>';
    }

    return equipment.map(item => `
        <div class="resource-item ${item.available > 0 ? 'available' : 'unavailable'}">
            <div class="resource-header">
                <span>${item.name}</span>
                <span>${item.available}/${item.quantity}</span>
            </div>
            <div>Status: ${item.condition}</div>
        </div>
    `).join('');
}

function renderVehicleList(vehicles) {
    if (!vehicles || vehicles.length === 0) {
        return '<p class="no-data">No vehicles available</p>';
    }

    return vehicles.map(vehicle => `
        <div class="resource-item ${vehicle.status === 'available' ? 'available' : 'unavailable'}">
            <div class="resource-header">
                <span>${vehicle.type} - ${vehicle.model}</span>
                <span>${vehicle.status}</span>
            </div>
            <div>Plate: ${vehicle.plate_number}</div>
        </div>
    `).join('');
}

function renderPersonnelList(personnel) {
    if (!personnel || personnel.length === 0) {
        return '<p class="no-data">No personnel available</p>';
    }

    return personnel.map(person => `
        <div class="resource-item ${person.status === 'on-duty' ? 'available' : 'unavailable'}">
            <div class="resource-header">
                <span>${person.name}</span>
                <span>${person.status}</span>
            </div>
            <div>Role: ${person.role}</div>
            ${person.speciality ? `<div>Specialty: ${person.speciality}</div>` : ''}
        </div>
    `).join('');
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

function showLoading() {
    const loadingEl = document.createElement('div');
    loadingEl.id = 'loading-overlay';
    loadingEl.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loadingEl);
}

function hideLoading() {
    const loadingEl = document.getElementById('loading-overlay');
    if (loadingEl) {
        loadingEl.remove();
    }
}

function showError(message) {
    const errorEl = document.createElement('div');
    errorEl.className = 'error-toast';
    errorEl.textContent = message;
    document.body.appendChild(errorEl);
    setTimeout(() => errorEl.remove(), 5000);
}