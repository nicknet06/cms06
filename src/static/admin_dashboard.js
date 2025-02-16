// Initialize map when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map
    const map = L.map('emergency-map').setView([38.2749497, 23.8102717], 7);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add markers for all emergency reports with locations
    const reports = document.querySelectorAll('.view-location-btn');
    reports.forEach(report => {
        const lat = parseFloat(report.getAttribute('data-lat'));
        const lng = parseFloat(report.getAttribute('data-lng'));
        if (lat && lng) {
            L.marker([lat, lng]).addTo(map);
        }
    });
});

// View report details
function viewReport(id) {
    // Implement view report functionality
    console.log(`Viewing report ${id}`);
    // You can implement a modal or redirect to a details page
}

// Show location on map
function showLocation(lat, lng) {
    // Center map on the location
    const map = document.querySelector('#emergency-map')._leaflet_map;
    map.setView([lat, lng], 13);
}

// Delete report
function deleteReport(id) {
    if (confirm('Are you sure you want to delete this report?')) {
        fetch(`/api/reports/${id}`, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.ok) {
                // Refresh the page to show updated data
                location.reload();
            } else {
                throw new Error('Failed to delete report');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to delete report. Please try again.');
        });
    }
}

// Auto-refresh the data every 30 seconds
setInterval(() => {
    location.reload();
}, 30000);