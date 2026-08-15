// Section Navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all menu items
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Add active class to clicked menu item
    event.target.classList.add('active');
    
    // Initialize map if zones section is shown
    if (sectionId === 'zones' && !window.adminMapInitialized) {
        initAdminMap();
    }
}

// Initialize Admin Map
let adminMap;
function initAdminMap() {
    adminMap = L.map('adminMap').setView([13.0827, 80.2707], 11);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(adminMap);
    
    window.adminMapInitialized = true;
    
    // Load flood data
    loadFloodDataForAdmin();
}

// Load Flood Data for Admin
function loadFloodDataForAdmin() {
    fetch('../data/processed/chennai_flood_risk_with_water.geojson')
        .then(response => response.json())
        .then(data => {
            let stats = { safe: 0, moderate: 0, high: 0, severe: 0, total: 0 };
            
            data.features.forEach(feature => {
                const risk = feature.properties.flood_risk;
                stats.total++;
                if (risk === 'Low') stats.safe++;
                else if (risk === 'Moderate') stats.moderate++;
                else if (risk === 'High') stats.high++;
                else if (risk === 'Severe') stats.severe++;
            });
            
            // Update stats
            document.getElementById('totalZonesAdmin').textContent = stats.total;
            document.getElementById('highRiskAdmin').textContent = stats.high + stats.severe;
            document.getElementById('safeZonesAdmin').textContent = stats.safe;
            
            // Add to map
            if (adminMap) {
                L.geoJSON(data, {
                    style: function(feature) {
                        const colors = {
                            'Low': '#10b981',
                            'Moderate': '#f59e0b',
                            'High': '#f97316',
                            'Severe': '#ef4444'
                        };
                        return {
                            fillColor: colors[feature.properties.flood_risk] || '#6b7280',
                            weight: 0,
                            opacity: 0,
                            fillOpacity: 0.7
                        };
                    }
                }).addTo(adminMap);
            }
            
            // Initialize charts
            initCharts(stats);
        })
        .catch(error => console.error('Error loading data:', error));
}

// Initialize Charts
function initCharts(stats) {
    // Risk Distribution Chart
    const riskCtx = document.getElementById('riskChart');
    if (riskCtx) {
        new Chart(riskCtx, {
            type: 'doughnut',
            data: {
                labels: ['Safe', 'Moderate', 'High', 'Severe'],
                datasets: [{
                    data: [stats.safe, stats.moderate, stats.high, stats.severe],
                    backgroundColor: ['#10b981', '#f59e0b', '#f97316', '#ef4444']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Trend Chart
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'High Risk Zones',
                    data: [12, 19, 15, 25, 22, 18, 20],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Alert Functions
function sendMassAlert() {
    if (confirm('Send mass alert to all users?')) {
        alert('Mass alert sent successfully!');
    }
}

function scheduleAlert() {
    alert('Schedule alert feature coming soon!');
}

function createAlert(event) {
    event.preventDefault();
    alert('Alert created and sent successfully!');
    event.target.reset();
}

// Export Functions
function exportZones() {
    alert('Exporting zone data...');
}

function generateReport() {
    alert('Generating report...');
}

function downloadReport() {
    alert('Downloading PDF report...');
}

// User Management
function addUser() {
    alert('Add user form coming soon!');
}

// Contact Management
function addContact() {
    alert('Add contact form coming soon!');
}

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        sessionStorage.removeItem('adminLoggedIn');
        sessionStorage.removeItem('adminUsername');
        window.location.href = 'login.html';
    }
}

// Search and Filter
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchZone');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            console.log('Searching:', this.value);
        });
    }
    
    const filterSelect = document.getElementById('filterRisk');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            console.log('Filtering by:', this.value);
        });
    }
    
    // Load initial data
    loadFloodDataForAdmin();
});
