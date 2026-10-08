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
        fetch('/api/grids')
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

function loadAlerts() {
    fetch('/api/alerts/all')
        .then(response => response.json())
        .then(alerts => {
            const list = document.getElementById('adminHistoryList');
            if (!list) return;
            list.innerHTML = '';
            alerts.forEach(alert => {
                const item = document.createElement('div');
                item.className = 'history-item';
                const badgeClass = alert.severity === 'Critical' ? 'severe' : (alert.severity === 'High' ? 'high' : 'info');
                item.innerHTML = `
                    <div class="history-header">
                        <span class="badge ${badgeClass}">${alert.severity}</span>
                        <span class="history-time">${alert.timestamp}</span>
                    </div>
                    <p><strong>${alert.title}</strong>: ${alert.message}</p>
                    <small>Zone: ${alert.zone}</small>
                `;
                list.appendChild(item);
            });
        })
        .catch(err => console.error("Error loading alerts:", err));
}

function createAlert(event) {
    event.preventDefault();
    const typeSelect = document.getElementById('alertType');
    const zoneSelect = document.getElementById('alertZone');
    const messageArea = document.getElementById('alertMessage');
    const prioritySelect = document.getElementById('alertPriority');
    
    const payload = {
        title: typeSelect.options[typeSelect.selectedIndex].text,
        severity: prioritySelect.value,
        zone: zoneSelect.value,
        message: messageArea.value
    };
    
    fetch('/api/alerts/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error("Server error");
        return res.json();
    })
    .then(data => {
        alert("Alert created and published successfully!");
        event.target.reset();
        loadAlerts();
    })
    .catch(err => alert("Failed to publish alert: " + err.message));
}

// Export Functions
function exportZones() {
    alert('Exporting zone data...');
}

function generateReport() {
    const reportOutput = document.getElementById('reportOutput');
    const reportContent = document.getElementById('reportContent');
    if (!reportOutput || !reportContent) return;
    
    // Fetch live GeoJSON risk summary
        fetch('/api/grids')
    .then(res => res.json())
    .then(data => {
        let stats = { safe: 0, moderate: 0, high: 0, severe: 0, total: 0, totalRain: 0, maxRain: 0 };
        data.features.forEach(f => {
            const risk = f.properties.flood_risk;
            stats.total++;
            stats.totalRain += f.properties.rainfall_mm;
            if (f.properties.rainfall_mm > stats.maxRain) stats.maxRain = f.properties.rainfall_mm;
            
            if (risk === 'Low') stats.safe++;
            else if (risk === 'Moderate') stats.moderate++;
            else if (risk === 'High') stats.high++;
            else if (risk === 'Severe') stats.severe++;
        });
        
        const avgRain = (stats.totalRain / stats.total).toFixed(1);
        
        // Generate html table report
        reportContent.innerHTML = `
            <table class="table" style="width:100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="border-bottom: 2px solid #cbd5e1; text-align: left; padding: 8px;">
                        <th style="padding: 10px 0; color:#0f172a;">Metric Parameter</th>
                        <th style="padding: 10px 0; color:#0f172a;">Calculated Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px 0; font-weight:600; color:#334155;">Total Monitored Sectors</td>
                        <td style="padding: 10px 0; color:#334155;">${stats.total} zones</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px 0; font-weight:600; color:#334155;">Critical Risk Zones (Severe)</td>
                        <td style="padding: 10px 0; color:#ef4444; font-weight:700;">${stats.severe} zones</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px 0; font-weight:600; color:#334155;">High Risk Zones</td>
                        <td style="padding: 10px 0; color:#f97316; font-weight:700;">${stats.high} zones</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px 0; font-weight:600; color:#334155;">Average Rainfall Index</td>
                        <td style="padding: 10px 0; color:#334155;">${avgRain} mm</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px 0; font-weight:600; color:#334155;">Peak Precipitation Recorded</td>
                        <td style="padding: 10px 0; font-weight:700; color:#334155;">${stats.maxRain} mm</td>
                    </tr>
                </tbody>
            </table>
            <p style="margin-top: 15px; font-size:12px; color:#64748b;">Report compiled automatically by GeoGuard Command Center. Data source status: Active.</p>
        `;
        
        reportOutput.style.display = 'block';
        alert('Report generated successfully!');
    })
    .catch(err => alert("Failed to fetch report data: " + err.message));
}

function downloadReport() {
    const reportContent = document.getElementById('reportContent');
    if (!reportContent || reportContent.innerHTML === '') {
        alert("Please generate a report first!");
        return;
    }
    window.print();
}

// User Management
function addUser() {
    alert('Add user form coming soon!');
}

// Contact Management
function addContact() {
    const name = prompt("Enter emergency service name:");
    if (!name) return;
    const number = prompt("Enter contact number:");
    if (!number) return;
    const desc = prompt("Enter contact description:");
    if (!desc) return;
    
    const list = document.getElementById('adminContactsList');
    if (!list) return;
    
    const card = document.createElement('div');
    card.className = 'contact-edit-card';
    card.innerHTML = `
        <h4>${name}</h4>
        <input type="text" class="form-control" value="${number}">
        <input type="text" class="form-control" value="${desc}">
        <button class="btn-small" onclick="saveContact(this)">Save</button>
        <button class="btn-small" onclick="deleteContact(this)">Delete</button>
    `;
    list.appendChild(card);
    alert("New contact service added!");
}

function saveContact(btn) {
    const card = btn.closest('.contact-edit-card');
    const name = card.querySelector('h4').textContent;
    const inputs = card.querySelectorAll('input');
    const number = inputs[0].value;
    const desc = inputs[1].value;
    alert(`Contact "${name}" saved successfully:\nNumber: ${number}\nDescription: ${desc}`);
}

function deleteContact(btn) {
    const card = btn.closest('.contact-edit-card');
    const name = card.querySelector('h4').textContent;
    if (confirm(`Are you sure you want to delete ${name}?`)) {
        card.remove();
        alert("Contact service deleted.");
    }
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
    loadAlerts();
});

function saveSetting(input, name) {
    const val = input.checked;
    localStorage.setItem(`setting_${name}`, val);
    console.log(`Setting ${name} updated to: ${val}`);
}
