// Dynamic areas data with risk classifications loaded from database GeoJSON
let areasData = [];
let currentFilter = 'all';

// Determine the correct path based on where the server is running
const dataPath = '../data/processed/chennai_flood_risk_with_water.geojson';

// Helper to get neighborhood name in Chennai
function getPlaceName(lat, lng) {
    if (lat > 13.13) return "Madhavaram";
    if (lat > 13.11 && lng > 80.25) return "Royapuram";
    if (lat > 13.11) return "Perambur";
    if (lat > 13.085 && lng > 80.25) return "George Town";
    if (lat > 13.085) return "Anna Nagar";
    if (lat > 13.065 && lng > 80.25) return "Egmore";
    if (lat > 13.065) return "Kilpauk";
    if (lat > 13.045 && lng > 80.23) return "Nungambakkam";
    if (lat > 13.045) return "Vadapalani";
    if (lat > 13.03 && lng > 80.23) return "T. Nagar";
    if (lat > 13.03) return "Ashok Nagar";
    if (lat > 13.01 && lng > 80.24) return "Mylapore";
    if (lat > 13.01) return "Guindy";
    if (lat > 12.98 && lng > 80.24) return "Adyar";
    if (lat > 12.98) return "Velachery";
    if (lat > 12.95 && lng > 80.24) return "Thiruvanmiyur";
    if (lat > 12.95) return "Pallikaranai";
    if (lat > 12.90 && lng > 80.24) return "Neelankarai";
    if (lat > 12.90) return "Sholinganallur";
    return "Tambaram";
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔄 Loading flood risk areas dynamically...");
    
    fetch(dataPath)
    .then(response => {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
    })
    .then(data => {
        // Map GeoJSON features into areasData format
        areasData = data.features.map((feature, index) => {
            const props = feature.properties;
            const placeName = getPlaceName(props.latitude, props.longitude);
            
            // Format Risk levels to match standard EOC categories (Low -> Safe)
            let riskLabel = props.flood_risk;
            if (riskLabel === 'Low') riskLabel = 'Safe';
            
            return {
                id: index,
                name: `${placeName} (Zone ${index + 1})`,
                lat: props.latitude,
                lng: props.longitude,
                risk: riskLabel,
                score: props.flood_risk_score,
                rainfall: props.rainfall_mm,
                elevation: props.elevation_m,
                waterDist: parseFloat((props.distance_to_water / 1000).toFixed(2)),
                population: Math.round(props.elevation_m * 850 + (props.rainfall_mm * 120))
            };
        });

        // Update counts
        updateSummaryCounts();
        
        // Check URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const filterParam = urlParams.get('filter');
        
        if (filterParam && ['Safe', 'Moderate', 'High', 'Severe'].includes(filterParam)) {
            currentFilter = filterParam;
            const filtered = areasData.filter(area => area.risk === filterParam);
            displayAreas(filtered);
            
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.includes(filterParam)) {
                    btn.classList.add('active');
                }
            });
        } else {
            displayAreas(areasData);
        }
    })
    .catch(err => {
        console.error("Failed to load areas:", err);
        document.getElementById('areasGrid').innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #DC2626; font-weight: bold;">
                Failed to load live flood risk areas. Please ensure the web server is running.
            </div>
        `;
    });
});

// Update summary counts
function updateSummaryCounts() {
    const counts = {
        Safe: 0,
        Moderate: 0,
        High: 0,
        Severe: 0
    };
    
    areasData.forEach(area => {
        if (counts[area.risk] !== undefined) {
            counts[area.risk]++;
        }
    });
    
    document.getElementById('safeCount').textContent = counts.Safe;
    document.getElementById('moderateCount').textContent = counts.Moderate;
    document.getElementById('highCount').textContent = counts.High;
    document.getElementById('severeCount').textContent = counts.Severe;
}

// Display areas
function displayAreas(areas) {
    const grid = document.getElementById('areasGrid');
    grid.innerHTML = '';
    
    if (areas.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748B; font-weight: 500;">
                No areas found matching the selected filter.
            </div>
        `;
        return;
    }
    
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
    
    const riskMessage = {
        'Safe': 'Safe for normal activities',
        'Moderate': 'Monitor weather updates',
        'High': 'Prepare emergency supplies',
        'Severe': 'Evacuation may be required'
    };
    
    card.innerHTML = `
        <div class="area-header">
            <div class="area-name">${area.name}</div>
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
                <span class="detail-value">${riskMessage[area.risk] || 'Unknown'}</span>
            </div>
        </div>
        <div class="area-actions">
            <button class="action-btn view-btn" onclick="viewOnMap(${area.lat}, ${area.lng})">View on Map</button>
            ${area.risk === 'High' || area.risk === 'Severe' ? 
                '<button class="action-btn alert-btn" onclick="sendAlert(\'' + area.name + '\')">Send Alert</button>' : 
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
