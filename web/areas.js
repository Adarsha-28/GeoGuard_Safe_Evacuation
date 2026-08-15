// Comprehensive area data with risk classifications
const areasData = [
    // SEVERE RISK AREAS (4)
    { name: "Sholinganallur", lat: 12.9010, lng: 80.2279, risk: "Severe", score: 0.89, rainfall: 285, elevation: 2, waterDist: 0.3, population: 85000 },
    { name: "ECR (East Coast Road)", lat: 12.8500, lng: 80.2500, risk: "Severe", score: 0.85, rainfall: 290, elevation: 3, waterDist: 0.1, population: 45000 },
    { name: "Besant Nagar", lat: 13.0001, lng: 80.2668, risk: "Severe", score: 0.82, rainfall: 275, elevation: 4, waterDist: 0.2, population: 62000 },
    { name: "Santhome", lat: 13.0338, lng: 80.2771, risk: "Severe", score: 0.78, rainfall: 270, elevation: 5, waterDist: 0.4, population: 48000 },
    
    // HIGH RISK AREAS (13)
    { name: "Velachery", lat: 12.9750, lng: 80.2200, risk: "High", score: 0.72, rainfall: 265, elevation: 8, waterDist: 0.8, population: 125000 },
    { name: "Adyar", lat: 13.0067, lng: 80.2570, risk: "High", score: 0.70, rainfall: 260, elevation: 7, waterDist: 0.5, population: 95000 },
    { name: "Pallikaranai", lat: 12.9450, lng: 80.2050, risk: "High", score: 0.68, rainfall: 268, elevation: 6, waterDist: 0.6, population: 78000 },
    { name: "Perungudi", lat: 12.9610, lng: 80.2440, risk: "High", score: 0.67, rainfall: 262, elevation: 9, waterDist: 0.7, population: 68000 },
    { name: "Kotturpuram", lat: 13.0200, lng: 80.2450, risk: "High", score: 0.65, rainfall: 258, elevation: 10, waterDist: 0.9, population: 52000 },
    { name: "Mylapore", lat: 13.0339, lng: 80.2619, risk: "High", score: 0.64, rainfall: 255, elevation: 11, waterDist: 1.0, population: 88000 },
    { name: "Mandaveli", lat: 13.0280, lng: 80.2580, risk: "High", score: 0.63, rainfall: 254, elevation: 12, waterDist: 1.1, population: 45000 },
    { name: "Thiruvanmiyur", lat: 12.9820, lng: 80.2590, risk: "High", score: 0.62, rainfall: 252, elevation: 13, waterDist: 0.8, population: 72000 },
    { name: "Neelankarai", lat: 12.9490, lng: 80.2590, risk: "High", score: 0.61, rainfall: 250, elevation: 14, waterDist: 0.5, population: 38000 },
    { name: "Injambakkam", lat: 12.9100, lng: 80.2450, risk: "High", score: 0.60, rainfall: 248, elevation: 15, waterDist: 0.6, population: 28000 },
    { name: "Palavakkam", lat: 12.9650, lng: 80.2550, risk: "High", score: 0.58, rainfall: 246, elevation: 16, waterDist: 0.4, population: 32000 },
    { name: "Taramani", lat: 12.9910, lng: 80.2430, risk: "High", score: 0.57, rainfall: 244, elevation: 17, waterDist: 1.2, population: 58000 },
    { name: "Guindy", lat: 13.0067, lng: 80.2206, risk: "High", score: 0.56, rainfall: 242, elevation: 18, waterDist: 1.5, population: 65000 },
    
    // MODERATE RISK AREAS (13)
    { name: "T Nagar", lat: 13.0418, lng: 80.2341, risk: "Moderate", score: 0.48, rainfall: 235, elevation: 22, waterDist: 2.0, population: 145000 },
    { name: "Nungambakkam", lat: 13.0569, lng: 80.2425, risk: "Moderate", score: 0.46, rainfall: 232, elevation: 24, waterDist: 2.2, population: 82000 },
    { name: "Egmore", lat: 13.0732, lng: 80.2609, risk: "Moderate", score: 0.44, rainfall: 230, elevation: 26, waterDist: 2.5, population: 95000 },
    { name: "Kodambakkam", lat: 13.0524, lng: 80.2247, risk: "Moderate", score: 0.42, rainfall: 228, elevation: 28, waterDist: 2.8, population: 78000 },
    { name: "Saidapet", lat: 13.0210, lng: 80.2231, risk: "Moderate", score: 0.40, rainfall: 226, elevation: 30, waterDist: 1.8, population: 68000 },
    { name: "Chromepet", lat: 12.9516, lng: 80.1462, risk: "Moderate", score: 0.38, rainfall: 224, elevation: 32, waterDist: 3.0, population: 92000 },
    { name: "Perambur", lat: 13.1143, lng: 80.2378, risk: "Moderate", score: 0.36, rainfall: 222, elevation: 34, waterDist: 3.2, population: 105000 },
    { name: "Royapuram", lat: 13.1067, lng: 80.2933, risk: "Moderate", score: 0.35, rainfall: 220, elevation: 36, waterDist: 1.0, population: 72000 },
    { name: "Tondiarpet", lat: 13.1167, lng: 80.2833, risk: "Moderate", score: 0.34, rainfall: 218, elevation: 38, waterDist: 1.2, population: 58000 },
    { name: "Madhavaram", lat: 13.1482, lng: 80.2314, risk: "Moderate", score: 0.32, rainfall: 216, elevation: 40, waterDist: 3.5, population: 88000 },
    { name: "Ambattur", lat: 13.1143, lng: 80.1548, risk: "Moderate", score: 0.30, rainfall: 214, elevation: 42, waterDist: 4.0, population: 125000 },
    { name: "Avadi", lat: 13.1067, lng: 80.1018, risk: "Moderate", score: 0.28, rainfall: 212, elevation: 45, waterDist: 5.0, population: 98000 },
    { name: "Porur", lat: 13.0381, lng: 80.1570, risk: "Moderate", score: 0.26, rainfall: 210, elevation: 48, waterDist: 4.5, population: 85000 },
    
    // LOW RISK AREAS (4)
    { name: "Anna Nagar", lat: 13.0850, lng: 80.2101, risk: "Low", score: 0.22, rainfall: 205, elevation: 52, waterDist: 5.5, population: 115000 },
    { name: "Tambaram", lat: 12.9249, lng: 80.1000, risk: "Low", score: 0.18, rainfall: 200, elevation: 55, waterDist: 6.0, population: 145000 },
    { name: "Ashok Nagar", lat: 13.0358, lng: 80.2101, risk: "Low", score: 0.15, rainfall: 195, elevation: 58, waterDist: 6.5, population: 68000 },
    { name: "KK Nagar", lat: 13.0381, lng: 80.2020, risk: "Low", score: 0.12, rainfall: 190, elevation: 60, waterDist: 7.0, population: 72000 }
];

let currentFilter = 'all';

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    updateSummaryCounts();
    
    // Check for filter parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const filterParam = urlParams.get('filter');
    
    if (filterParam && ['Low', 'Moderate', 'High', 'Severe'].includes(filterParam)) {
        // Apply filter from URL
        currentFilter = filterParam;
        const filtered = areasData.filter(area => area.risk === filterParam);
        displayAreas(filtered);
        
        // Update active button
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.textContent.includes(filterParam === 'Low' ? 'Safe' : filterParam)) {
                btn.classList.add('active');
            }
        });
    } else {
        displayAreas(areasData);
    }
});

// Update summary counts
function updateSummaryCounts() {
    const counts = {
        Low: 0,
        Moderate: 0,
        High: 0,
        Severe: 0
    };
    
    areasData.forEach(area => {
        counts[area.risk]++;
    });
    
    document.getElementById('safeCount').textContent = counts.Low;
    document.getElementById('moderateCount').textContent = counts.Moderate;
    document.getElementById('highCount').textContent = counts.High;
    document.getElementById('severeCount').textContent = counts.Severe;
}

// Display areas
function displayAreas(areas) {
    const grid = document.getElementById('areasGrid');
    grid.innerHTML = '';
    
    areas.forEach(area => {
        const card = createAreaCard(area);
        grid.appendChild(card);
    });
}

// Create area card
function createAreaCard(area) {
    const card = document.createElement('div');
    card.className = `area-card ${area.risk}`;
    card.setAttribute('data-risk', area.risk);
    card.setAttribute('data-name', area.name.toLowerCase());
    
    const riskIcon = {
        'Low': '✅',
        'Moderate': '⚠️',
        'High': '🔶',
        'Severe': '🚨'
    };
    
    const riskMessage = {
        'Low': 'Safe for normal activities',
        'Moderate': 'Monitor weather updates',
        'High': 'Prepare emergency supplies',
        'Severe': 'Evacuation may be required'
    };
    
    card.innerHTML = `
        <div class="area-header">
            <div class="area-name">${riskIcon[area.risk]} ${area.name}</div>
            <div class="risk-badge ${area.risk}">${area.risk}</div>
        </div>
        <div class="area-details">
            <div class="detail-row">
                <span class="detail-label">Risk Score:</span>
                <span class="detail-value">${area.score.toFixed(2)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Rainfall:</span>
                <span class="detail-value">${area.rainfall} mm</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Elevation:</span>
                <span class="detail-value">${area.elevation} m</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Water Distance:</span>
                <span class="detail-value">${area.waterDist} km</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Population:</span>
                <span class="detail-value">${area.population.toLocaleString()}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span class="detail-value">${riskMessage[area.risk]}</span>
            </div>
        </div>
        <div class="area-actions">
            <button class="action-btn view-btn" onclick="viewOnMap(${area.lat}, ${area.lng})">📍 View on Map</button>
            ${area.risk === 'High' || area.risk === 'Severe' ? 
                '<button class="action-btn alert-btn" onclick="sendAlert(\'' + area.name + '\')">🚨 Send Alert</button>' : 
                ''}
        </div>
    `;
    
    return card;
}

// Filter areas
function filterAreas(risk) {
    currentFilter = risk;
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Filter and display
    const filtered = risk === 'all' ? areasData : areasData.filter(area => area.risk === risk);
    displayAreas(filtered);
    
    // Update URL without reloading
    const newUrl = risk === 'all' ? 'areas.html' : `areas.html?filter=${risk}`;
    window.history.pushState({filter: risk}, '', newUrl);
}

// Search areas
function searchAreas() {
    const searchTerm = document.getElementById('areaSearch').value.toLowerCase();
    const cards = document.querySelectorAll('.area-card');
    
    cards.forEach(card => {
        const name = card.getAttribute('data-name');
        if (name.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// View on map
function viewOnMap(lat, lng) {
    window.location.href = `index.html?lat=${lat}&lng=${lng}&zoom=15`;
}

// Send alert
function sendAlert(areaName) {
    alert(`🚨 Emergency Alert sent to residents of ${areaName}!\n\nAlert Message:\n- Flood risk is HIGH\n- Stay indoors if possible\n- Keep emergency supplies ready\n- Monitor official updates\n- Be prepared to evacuate if instructed`);
}
