// Initialize map centered on Chennai
const map = L.map('map').setView([13.0827, 80.2707], 11);

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
}).addTo(map);

// Chennai area names for place name generation
const chennaiAreas = [
    "T. Nagar", "Anna Nagar", "Adyar", "Velachery", "Tambaram", "Porur",
    "Guindy", "Mylapore", "Nungambakkam", "Egmore", "Perungudi", "Sholinganallur",
    "OMR", "ECR", "Pallavaram", "Chromepet", "Saidapet", "Kodambakkam",
    "Ashok Nagar", "KK Nagar", "Vadapalani", "Virugambakkam", "Koyambedu",
    "Aminjikarai", "Kilpauk", "Chetpet", "Teynampet", "Alwarpet", "Mandaveli",
    "Besant Nagar", "Thiruvanmiyur", "Taramani", "Kotturpuram", "Santhome"
];

// Store loaded GeoJSON data globally
let floodData = null;
let userLocationMarker = null;
let shelterMarkers = [];
let allShelterMarkers = [];

// Generate place name from coordinates using hash
function getPlaceName(lat, lon) {
    const hash = Math.floor(Math.abs((lat * 1000 + lon * 1000)) % chennaiAreas.length);
    return chennaiAreas[hash];
}

// Get color based on risk level
function getRiskColor(risk) {
    const colors = {
        'Low': '#10b981',
        'Moderate': '#f59e0b',
        'High': '#f97316',
        'Severe': '#ef4444'
    };
    return colors[risk] || '#6b7280';
}

// Statistics object with default counts
let stats = {
    safe: 4,
    moderate: 13,
    high: 13,
    severe: 4,
    total: 34
};

// Function to update UI with statistics
function updateStatistics() {
    document.getElementById('totalZones').textContent = stats.total;
    document.getElementById('highRisk').textContent = stats.high + stats.severe;
    document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
    
    // Update metric cards dynamically
    const safeEl = document.getElementById('safeZonesMetric');
    const modEl = document.getElementById('moderateRiskMetric');
    const highEl = document.getElementById('highRiskMetric');
    const sevEl = document.getElementById('severeRiskMetric');
    
    if (safeEl) safeEl.textContent = stats.safe;
    if (modEl) modEl.textContent = stats.moderate;
    if (highEl) highEl.textContent = stats.high;
    if (sevEl) sevEl.textContent = stats.severe;
}

// Function to generate alerts
function generateAlerts() {
    const alertsList = document.getElementById('alertsList');
    alertsList.innerHTML = '';
    
    if (stats.severe > 0) {
        alertsList.innerHTML += `<div class="alert-item">⚠️ ${stats.severe} zones in SEVERE risk</div>`;
    }
    if (stats.high > 0) {
        alertsList.innerHTML += `<div class="alert-item">⚠️ ${stats.high} zones in HIGH risk</div>`;
    }
    if (stats.severe === 0 && stats.high === 0) {
        alertsList.innerHTML = '<div style="opacity: 0.7; padding: 12px;">✅ No active alerts</div>';
    }
}

// Function to create popup content
function createPopupContent(props, placeName) {
    // Use actual data from GeoJSON properties
    const riskLevel = props.flood_risk;
    const riskScore = props.flood_risk_score;
    
    return `
        <div class="popup-title">${placeName}</div>
        <div class="popup-info">
            <div><strong>Risk Level:</strong> <span style="color: ${getRiskColor(riskLevel)}; font-weight: bold;">${riskLevel}</span></div>
            <div><strong>Risk Score:</strong> ${(riskScore * 100).toFixed(1)}%</div>
            <div><strong>Rainfall:</strong> ${props.rainfall_mm} mm</div>
            <div><strong>Elevation:</strong> ${props.elevation_m} m</div>
            <div><strong>Distance to Water:</strong> ${(props.distance_to_water / 1000).toFixed(2)} km</div>
            <hr style="margin: 10px 0; border: none; border-top: 1px solid #e2e8f0;">
            <div style="margin-top: 10px; font-size: 12px;">
                ${riskLevel === 'Severe' ? 
                    '<strong style="color: #ef4444;">🚨 SEVERE RISK! Immediate evacuation recommended. Seek higher ground!</strong>' : 
                    riskLevel === 'High' ?
                    '<strong style="color: #f97316;">🔶 HIGH RISK! Prepare emergency supplies and monitor updates.</strong>' :
                    riskLevel === 'Moderate' ?
                    '<strong style="color: #f59e0b;">⚠️ Moderate risk. Monitor weather updates regularly.</strong>' :
                    riskLevel === 'Low' ?
                    '<strong style="color: #10b981;">✅ Area is relatively safe from flooding.</strong>' :
                    ''}
            </div>
        </div>
    `;
}

// Load and display GeoJSON data
console.log('🔄 Loading flood risk data...');

// Determine the correct path based on where the server is running
const dataPath = '../data/processed/chennai_flood_risk_with_water.geojson';

fetch(dataPath)
    .then(response => {
        console.log('📡 Response received:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    })
    .then(data => {
        console.log('✅ Data loaded successfully!');
        console.log('📊 Total features:', data.features.length);
        
        // Count statistics - reset to 0 first
        let tempStats = {
            safe: 0,
            moderate: 0,
            high: 0,
            severe: 0,
            total: 0
        };
        
        data.features.forEach(feature => {
            const risk = feature.properties.flood_risk;
            tempStats.total++;
            
            if (risk === 'Low') {
                tempStats.safe++;
            } else if (risk === 'Moderate') {
                tempStats.moderate++;
            } else if (risk === 'High') {
                tempStats.high++;
            } else if (risk === 'Severe') {
                tempStats.severe++;
            }
        });
        
        // Update stats with actual data
        stats = tempStats;
        
        console.log('📈 Statistics:', stats);
        
        // Update UI
        updateStatistics();
        generateAlerts();
        
        // Add GeoJSON layer to map
        const geoJsonLayer = L.geoJSON(data, {
            style: function(feature) {
                return {
                    fillColor: getRiskColor(feature.properties.flood_risk),
                    weight: 0,  // Remove grid lines
                    opacity: 0,  // Remove border
                    color: 'transparent',  // Transparent border
                    fillOpacity: 0.7  // Slightly more opaque for better visibility
                };
            },
            onEachFeature: function(feature, layer) {
                const props = feature.properties;
                const placeName = getPlaceName(props.latitude, props.longitude);
                
                // Bind popup
                layer.bindPopup(createPopupContent(props, placeName));
                
                // Hover effects
                layer.on('mouseover', function() {
                    this.setStyle({
                        weight: 2,
                        opacity: 1,
                        color: '#fff',
                        fillOpacity: 0.9
                    });
                });
                
                layer.on('mouseout', function() {
                    this.setStyle({
                        weight: 0,
                        opacity: 0,
                        color: 'transparent',
                        fillOpacity: 0.7
                    });
                });
            }
        }).addTo(map);
        
        // Fit map to data bounds
        map.fitBounds(geoJsonLayer.getBounds());
        
        console.log('🗺️ Map rendered successfully!');
        
        // Store data globally
        floodData = data;
        
        // Initialize search and location features
        initializeSearchAndLocation();
        loadAllShelters();
    })
    .catch(error => {
        console.error('❌ Error loading data:', error);
        
        // Display user-friendly error message
        const alertsList = document.getElementById('alertsList');
        let errorMsg = '';
        
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMsg = `
                <div class="alert-item" style="line-height: 1.8;">
                    ⚠️ <strong>Cannot load data!</strong><br>
                    <small>Please ensure you're running a local server.</small><br><br>
                    <strong>Solution:</strong><br>
                    1. Stop current server (Ctrl+C)<br>
                    2. Run: <code>cd ..</code><br>
                    3. Run: <code>python -m http.server 8000</code><br>
                    4. Open: <code>http://localhost:8000/web/index.html</code>
                </div>
            `;
        } else if (error.message.includes('404')) {
            errorMsg = `
                <div class="alert-item" style="line-height: 1.8;">
                    ⚠️ <strong>Data file not found!</strong><br>
                    <small>The GeoJSON file is missing.</small><br><br>
                    Expected location:<br>
                    <code>data/processed/chennai_flood_risk_with_water.geojson</code>
                </div>
            `;
        } else {
            errorMsg = `
                <div class="alert-item" style="line-height: 1.8;">
                    ⚠️ <strong>Error:</strong> ${error.message}
                </div>
            `;
        }
        
        alertsList.innerHTML = errorMsg;
        
        // Update stats to show error state
        document.getElementById('totalZones').textContent = 'Error';
        document.getElementById('highRisk').textContent = '--';
    });

// Initialize Search and Location Features
function initializeSearchAndLocation() {
    const searchInput = document.getElementById('locationSearch');
    const searchResults = document.getElementById('searchResults');
    const myLocationBtn = document.getElementById('myLocationBtn');
    
    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            
            if (query.length < 2) {
                searchResults.classList.remove('active');
                searchResults.innerHTML = '';
                return;
            }
            
            // Filter Chennai areas
            const matches = chennaiAreas.filter(area => 
                area.toLowerCase().includes(query)
            );
            
            if (matches.length > 0) {
                searchResults.innerHTML = matches.map(area => 
                    `<div class="search-result-item" onclick="searchLocation('${area}')">${area}</div>`
                ).join('');
                searchResults.classList.add('active');
            } else {
                searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
                searchResults.classList.add('active');
            }
        });
        
        // Close search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.remove('active');
            }
        });
    }
    
    // My Location button
    if (myLocationBtn) {
        myLocationBtn.addEventListener('click', getMyLocation);
    }
}

// Search for a location
function searchLocation(locationName) {
    const searchResults = document.getElementById('searchResults');
    searchResults.classList.remove('active');
    document.getElementById('locationSearch').value = locationName;
    
    if (!floodData) {
        alert('Data not loaded yet. Please wait...');
        return;
    }
    
    // Find a feature that matches this location
    let foundFeature = null;
    let minDistance = Infinity;
    
    // Get approximate coordinates for the location
    const locationCoords = getLocationCoordinates(locationName);
    
    if (locationCoords) {
        // Find the closest zone to these coordinates
        floodData.features.forEach(feature => {
            const props = feature.properties;
            const distance = Math.sqrt(
                Math.pow(props.latitude - locationCoords.lat, 2) + 
                Math.pow(props.longitude - locationCoords.lng, 2)
            );
            
            if (distance < minDistance) {
                minDistance = distance;
                foundFeature = feature;
            }
        });
        
        if (foundFeature) {
            const props = foundFeature.properties;
            const locationData = getLocationCoordinates(locationName);
            
            // Zoom to location
            map.setView([props.latitude, props.longitude], 14);
            
            // Show popup with location-specific data
            const popupContent = `
                <div class="popup-title">${locationName}</div>
                <div class="popup-info">
                    <div><strong>Risk Level:</strong> <span style="color: ${getRiskColor(locationData.risk)}; font-weight: bold;">${locationData.risk}</span></div>
                    <div><strong>Risk Score:</strong> ${(locationData.score * 100).toFixed(1)}%</div>
                    <div><strong>Status:</strong> ${locationData.risk === 'Low' ? '✅ Safe' : locationData.risk === 'Moderate' ? '⚠️ Caution' : '🚨 High Risk'}</div>
                    <div><strong>Rainfall:</strong> ${props.rainfall_mm} mm</div>
                    <div><strong>Elevation:</strong> ${props.elevation_m} m</div>
                    <div><strong>Distance to Water:</strong> ${(props.distance_to_water / 1000).toFixed(2)} km</div>
                    <hr style="margin: 10px 0; border: none; border-top: 1px solid #e2e8f0;">
                    <div style="margin-top: 10px; font-size: 12px;">
                        ${locationData.risk === 'Severe' || locationData.risk === 'High' ? 
                            '<strong style="color: #ef4444;">⚠️ Flood risk detected! Stay alert and follow safety guidelines.</strong>' : 
                            locationData.risk === 'Moderate' ?
                            '<strong style="color: #f59e0b;">⚠️ Moderate risk. Monitor weather updates.</strong>' :
                            '<strong style="color: #10b981;">✅ Area is relatively safe from flooding.</strong>'}
                    </div>
                </div>
            `;
            L.popup()
                .setLatLng([props.latitude, props.longitude])
                .setContent(popupContent)
                .openOn(map);
            
            // Add marker
            if (userLocationMarker) {
                map.removeLayer(userLocationMarker);
            }
            
            userLocationMarker = L.marker([props.latitude, props.longitude], {
                icon: L.divIcon({
                    className: 'custom-marker',
                    html: '📍',
                    iconSize: [30, 30]
                })
            }).addTo(map);
            
            displayNearestShelters(props.latitude, props.longitude);
        }
    }
}

// Get approximate coordinates for Chennai locations
function getLocationCoordinates(locationName) {
    const locations = {
        "T. Nagar": { lat: 13.0418, lng: 80.2341, risk: "Moderate", score: 0.42 },
        "Anna Nagar": { lat: 13.0850, lng: 80.2101, risk: "Low", score: 0.23 },
        "Adyar": { lat: 13.0067, lng: 80.2570, risk: "High", score: 0.68 },
        "Velachery": { lat: 12.9750, lng: 80.2210, risk: "High", score: 0.71 },
        "Tambaram": { lat: 12.9229, lng: 80.1275, risk: "Low", score: 0.19 },
        "Porur": { lat: 13.0358, lng: 80.1597, risk: "Moderate", score: 0.38 },
        "Guindy": { lat: 13.0067, lng: 80.2206, risk: "Moderate", score: 0.45 },
        "Mylapore": { lat: 13.0339, lng: 80.2619, risk: "High", score: 0.62 },
        "Nungambakkam": { lat: 13.0569, lng: 80.2425, risk: "Moderate", score: 0.35 },
        "Egmore": { lat: 13.0732, lng: 80.2609, risk: "Moderate", score: 0.41 },
        "Perungudi": { lat: 12.9611, lng: 80.2417, risk: "High", score: 0.73 },
        "Sholinganallur": { lat: 12.9010, lng: 80.2279, risk: "Severe", score: 0.82 },
        "OMR": { lat: 12.9500, lng: 80.2200, risk: "High", score: 0.69 },
        "ECR": { lat: 12.8500, lng: 80.2500, risk: "Severe", score: 0.85 },
        "Pallavaram": { lat: 12.9675, lng: 80.1491, risk: "Moderate", score: 0.47 },
        "Chromepet": { lat: 12.9516, lng: 80.1462, risk: "Moderate", score: 0.44 },
        "Saidapet": { lat: 13.0210, lng: 80.2231, risk: "High", score: 0.58 },
        "Kodambakkam": { lat: 13.0515, lng: 80.2254, risk: "Moderate", score: 0.39 },
        "Ashok Nagar": { lat: 13.0358, lng: 80.2093, risk: "Low", score: 0.28 },
        "KK Nagar": { lat: 13.0381, lng: 80.2020, risk: "Low", score: 0.24 },
        "Vadapalani": { lat: 13.0504, lng: 80.2121, risk: "Moderate", score: 0.36 },
        "Virugambakkam": { lat: 13.0562, lng: 80.2029, risk: "Low", score: 0.22 },
        "Koyambedu": { lat: 13.0732, lng: 80.1948, risk: "Moderate", score: 0.43 },
        "Aminjikarai": { lat: 13.0732, lng: 80.2186, risk: "Moderate", score: 0.37 },
        "Kilpauk": { lat: 13.0791, lng: 80.2424, risk: "Moderate", score: 0.40 },
        "Chetpet": { lat: 13.0732, lng: 80.2424, risk: "Moderate", score: 0.38 },
        "Teynampet": { lat: 13.0389, lng: 80.2497, risk: "High", score: 0.55 },
        "Alwarpet": { lat: 13.0339, lng: 80.2497, risk: "High", score: 0.59 },
        "Mandaveli": { lat: 13.0281, lng: 80.2644, risk: "High", score: 0.64 },
        "Besant Nagar": { lat: 13.0006, lng: 80.2661, risk: "Severe", score: 0.78 },
        "Thiruvanmiyur": { lat: 12.9833, lng: 80.2611, risk: "High", score: 0.72 },
        "Taramani": { lat: 12.9915, lng: 80.2447, risk: "High", score: 0.67 },
        "Kotturpuram": { lat: 13.0167, lng: 80.2497, risk: "High", score: 0.61 },
        "Santhome": { lat: 13.0339, lng: 80.2775, risk: "Severe", score: 0.81 }
    };
    
    return locations[locationName] || null;
}

// Get My Location
function getMyLocation() {
    const btn = document.getElementById('myLocationBtn');
    btn.textContent = '⏳ Getting location...';
    btn.disabled = true;
    
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser');
        btn.textContent = '📍 My Location';
        btn.disabled = false;
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            console.log('Your location:', lat, lng);
            
            // Check if location is in Chennai area (approximate bounds)
            if (lat < 12.8 || lat > 13.3 || lng < 80.0 || lng > 80.3) {
                alert('⚠️ You are outside Chennai area. Showing nearest data...');
            }
            
            // Find nearest zone
            if (floodData) {
                let nearestFeature = null;
                let minDistance = Infinity;
                
                floodData.features.forEach(feature => {
                    const props = feature.properties;
                    const distance = Math.sqrt(
                        Math.pow(props.latitude - lat, 2) + 
                        Math.pow(props.longitude - lng, 2)
                    );
                    
                    if (distance < minDistance) {
                        minDistance = distance;
                        nearestFeature = feature;
                    }
                });
                
                if (nearestFeature) {
                    const props = nearestFeature.properties;
                    const placeName = getPlaceName(props.latitude, props.longitude);
                    
                    // Zoom to location
                    map.setView([lat, lng], 15);
                    
                    // Remove old marker
                    if (userLocationMarker) {
                        map.removeLayer(userLocationMarker);
                    }
                    
                    // Add marker at user's location
                    userLocationMarker = L.marker([lat, lng], {
                        icon: L.divIcon({
                            className: 'user-location-marker',
                            html: '<div style="background: #0ea5e9; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.5);"></div>',
                            iconSize: [20, 20]
                        })
                    }).addTo(map);
                    
                    // Show popup with flood risk
                    const popupContent = `
                        <div class="popup-title">📍 Your Location</div>
                        <div class="popup-info">
                            <div><strong>Nearest Area:</strong> ${placeName}</div>
                            <div><strong>Risk Level:</strong> <span style="color: ${getRiskColor(props.flood_risk)}">${props.flood_risk}</span></div>
                            <div><strong>Risk Score:</strong> ${(props.flood_risk_score * 100).toFixed(1)}%</div>
                            <div><strong>Elevation:</strong> ${props.elevation_m} m</div>
                            <div><strong>Distance to Water:</strong> ${(props.distance_to_water / 1000).toFixed(2)} km</div>
                            <hr style="margin: 10px 0; border: none; border-top: 1px solid #e2e8f0;">
                            <div style="margin-top: 10px;">
                                ${props.flood_risk === 'High' || props.flood_risk === 'Severe' ? 
                                    '<strong style="color: #ef4444;">⚠️ High flood risk in your area!</strong>' : 
                                    '<strong style="color: #10b981;">✅ Your area is relatively safe</strong>'}
                            </div>
                        </div>
                    `;
                    
                    L.popup()
                        .setLatLng([lat, lng])
                        .setContent(popupContent)
                        .openOn(map);
                    
                    // Update search input
                    document.getElementById('locationSearch').value = placeName;
                    
                    displayNearestShelters(lat, lng);
                }
            }
            
            btn.textContent = '📍 My Location';
            btn.disabled = false;
        },
        function(error) {
            console.error('Error getting location:', error);
            let errorMsg = 'Unable to get your location. ';
            
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg += 'Please allow location access.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg += 'Location information unavailable.';
                    break;
                case error.TIMEOUT:
                    errorMsg += 'Location request timed out.';
                    break;
                default:
                    errorMsg += 'Unknown error occurred.';
            }
            
            alert(errorMsg);
            btn.textContent = '📍 My Location';
            btn.disabled = false;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}


function loadAllShelters() {
    fetch('/api/shelters/all')
    .then(response => {
        if (!response.ok) throw new Error("Failed to fetch all shelters");
        return response.json();
    })
    .then(shelters => {
        // Clear existing markers if any
        allShelterMarkers.forEach(marker => map.removeLayer(marker));
        allShelterMarkers = [];

        shelters.forEach(shelter => {
            const facilitiesText = typeof shelter.facilities === 'string' ? shelter.facilities : (shelter.facilities || []).join(', ');
            const marker = L.marker([shelter.latitude, shelter.longitude], {
                icon: L.divIcon({
                    className: 'shelter-marker',
                    html: '🏛️',
                    iconSize: [30, 30]
                })
            }).addTo(map);

            marker.bindPopup(`
                <div class="popup-title">🏛️ ${shelter.name}</div>
                <div class="popup-info">
                    <div><strong>Available Capacity:</strong> ${shelter.availableCapacity} / ${shelter.capacity}</div>
                    <div><strong>Risk Level:</strong> <span style="color: ${getRiskColor(shelter.riskLevel)}; font-weight: bold;">${shelter.riskLevel}</span></div>
                    <div><strong>Facilities:</strong> ${facilitiesText}</div>
                    <div><strong>Contact:</strong> ${shelter.contact}</div>
                </div>
            `);
            marker.shelterId = shelter.id;
            allShelterMarkers.push(marker);
        });
    })
    .catch(error => {
        console.error('Error fetching all shelters:', error);
    });
}

function displayNearestShelters(lat, lng) {
    const sheltersList = document.getElementById('sheltersList');
    if (!sheltersList) return;
    
    fetch(`/api/shelters/nearby?lat=${lat}&lng=${lng}&radius=20`)
    .then(response => {
        if (!response.ok) throw new Error("Failed to fetch nearby shelters");
        return response.json();
    })
    .then(nearestShelters => {
        // Take top 3
        const topShelters = nearestShelters.slice(0, 3);
        
        if (topShelters.length === 0) {
            sheltersList.innerHTML = '<div style="opacity: 0.7; padding: 12px;">⚠️ No active shelters found nearby</div>';
            return;
        }
        
        sheltersList.innerHTML = topShelters.map((shelter, index) => {
            const facilitiesText = typeof shelter.facilities === 'string' ? shelter.facilities : (shelter.facilities || []).join(', ');
            return `
            <div class="shelter-item" onclick="focusShelter(${shelter.latitude}, ${shelter.longitude}, '${shelter.name.replace(/'/g, "\\'")}')"
                 style="cursor: pointer; background: rgba(255, 255, 255, 0.8); padding: 12px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #10b981; transition: all 0.3s;"
                 onmouseover="this.style.background='rgba(16, 185, 129, 0.1)'; this.style.transform='translateX(5px)';"
                 onmouseout="this.style.background='rgba(255, 255, 255, 0.8)'; this.style.transform='translateX(0)';">
                <div style="font-weight: bold; color: #0369a1; margin-bottom: 5px;">
                    ${index + 1}. ${shelter.name}
                </div>
                <div style="font-size: 12px; color: #64748b; margin-bottom: 3px;">
                    📍 ${shelter.distance.toFixed(2)} km away
                </div>
                <div style="font-size: 12px; color: #64748b; margin-bottom: 3px;">
                    👥 Available: <span style="font-weight: bold; color: ${shelter.availableCapacity === 0 ? '#ef4444' : '#10b981'};">${shelter.availableCapacity}</span> / ${shelter.capacity}
                </div>
                <div style="font-size: 11px; color: #64748b;">
                    ✅ ${facilitiesText}
                </div>
                <div style="font-size: 12px; color: #0ea5e9; margin-top: 5px;">
                    📞 ${shelter.contact}
                </div>
            </div>
            `;
        }).join('');
    })
    .catch(error => {
        console.error('Error fetching nearby shelters:', error);
        sheltersList.innerHTML = '<div style="opacity: 0.7; padding: 12px; color: #ef4444;">⚠️ Error loading nearby shelters</div>';
    });
}

function focusShelter(lat, lng, name) {
    map.setView([lat, lng], 15);
    
    allShelterMarkers.forEach(marker => {
        const markerLatLng = marker.getLatLng();
        if (Math.abs(markerLatLng.lat - lat) < 0.0001 && Math.abs(markerLatLng.lng - lng) < 0.0001) {
            marker.openPopup();
        }
    });
}

// Evacuation Route Logic
let activeRoutePolyline = null;
let currentCoords = null; // Stores currently selected coords (GPS or Demo)
let simulatedDemoLocation = null;
let currentSelectedShelter = null;

// Demo location coordinates

function triggerRandomLocation() {
    // Generate random coordinates within Chennai bounds
    const minLat = 12.92;
    const maxLat = 13.12;
    const minLng = 80.16;
    const maxLng = 80.27;
    
    const randomLat = Math.random() * (maxLat - minLat) + minLat;
    const randomLng = Math.random() * (maxLng - minLng) + minLng;
    
    const areaName = getPlaceName(randomLat, randomLng);
    const name = `${areaName} (Random)`;
    
    simulatedDemoLocation = { lat: randomLat, lng: randomLng, name: name };
    currentCoords = {
        latitude: randomLat,
        longitude: randomLng
    };
    
    document.getElementById('userLocationText').innerText = `${areaName} (${randomLat.toFixed(4)}, ${randomLng.toFixed(4)})`;
    updateUserLocationMarker(randomLat, randomLng, name);
    resetRouteDetails();
    
    // Auto trigger safe route finding
    findSafeRoute();
}

function updateUserLocationMarker(lat, lng, name) {
    if (userLocationMarker) {
        map.removeLayer(userLocationMarker);
    }
    userLocationMarker = L.marker([lat, lng], {
        icon: L.divIcon({
            className: 'user-location-marker',
            html: '📍',
            iconSize: [30, 30]
        })
    }).addTo(map);
    userLocationMarker.bindPopup(`<strong>Your Location:</strong><br>${name}`).openPopup();
    map.setView([lat, lng], 13);
}

function resetRouteDetails() {
    document.getElementById('routeDetails').style.display = 'none';
    document.getElementById('startEvacuationBtn').style.display = 'none';
    document.getElementById('recalculateRouteBtn').style.display = 'none';
    document.getElementById('findSafeRouteBtn').style.display = 'block';
    if (activeRoutePolyline) {
        map.removeLayer(activeRoutePolyline);
        activeRoutePolyline = null;
    }
}

// Override getMyLocation to store coordinates and work with the Evacuation panel
const originalGetMyLocation = getMyLocation;
getMyLocation = function() {
    simulatedDemoLocation = null;
    
    const btn = document.getElementById('myLocationBtn');
    btn.textContent = '⌛ Locating...';
    btn.disabled = true;
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            currentCoords = {
                latitude: lat,
                longitude: lng
            };
            
            document.getElementById('userLocationText').innerText = `GPS: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
            updateUserLocationMarker(lat, lng, "My GPS Location");
            
            // Call original handler to populate nearby list
            displayNearestShelters(lat, lng);
            
            btn.textContent = '📍 My Location';
            btn.disabled = false;
        },
        function(error) {
            console.error('Error getting location:', error);
            let errorMsg = 'Unable to get your location. ';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg += 'Please allow location access.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg += 'Location information unavailable.';
                    break;
                case error.TIMEOUT:
                    errorMsg += 'Location request timed out.';
                    break;
                default:
                    errorMsg += 'Unknown error occurred.';
            }
            alert(errorMsg);
            btn.textContent = '📍 My Location';
            btn.disabled = false;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
};

function findSafeRoute() {
    if (!currentCoords) {
        alert("Please determine your location first via GPS (My Location button) or the Demo Chennai Location dropdown.");
        return;
    }
    
    const findBtn = document.getElementById('findSafeRouteBtn');
    findBtn.innerText = "Calculating Safe Route...";
    findBtn.disabled = true;
    
    fetch('/api/routes/safe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentCoords)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Server error'); });
        }
        return response.json();
    })
    .then(data => {
        findBtn.innerText = "FIND SAFE ROUTE";
        findBtn.disabled = false;
        
        // Save current shelter info
        currentSelectedShelter = data.shelter;
        
        // Display route details
        document.getElementById('routeDetails').style.display = 'block';
        document.getElementById('recShelterName').innerText = `🏠 ${data.shelter.name}`;
        document.getElementById('recDistance').innerText = `${data.shelter.distance.toFixed(2)} km`;
        
        const durationMins = Math.round(data.route.duration / 60);
        document.getElementById('recTime').innerText = `${durationMins} mins`;
        
        const risk = data.shelter.riskLevel;
        const riskColor = getRiskColor(risk);
        document.getElementById('recRisk').innerHTML = `<span style="color: ${riskColor};">${risk}</span>`;
        
        const safetyScorePercent = Math.round(data.route.safetyScore * 100);
        document.getElementById('recSafety').innerText = `${safetyScorePercent}%`;
        document.getElementById('recCapacity').innerText = `${data.shelter.availableCapacity} / ${data.shelter.capacity}`;
        document.getElementById('recReason').innerText = `Reason: "${data.reason}"`;
        
        // Toggle buttons
        findBtn.style.display = 'none';
        document.getElementById('startEvacuationBtn').style.display = 'block';
        document.getElementById('recalculateRouteBtn').style.display = 'block';
        
        // Plot route polyline on map
        if (activeRoutePolyline) {
            map.removeLayer(activeRoutePolyline);
        }
        
        const coordinates = data.route.geometry.coordinates.map(coord => [coord[1], coord[0]]);
        
        // Draw double polyline for a nice glowing Google Maps routing look
        activeRoutePolyline = L.featureGroup([
            L.polyline(coordinates, { color: '#1e3a8a', weight: 10, opacity: 0.5, lineCap: 'round', lineJoin: 'round' }),
            L.polyline(coordinates, { color: '#3b82f6', weight: 6, opacity: 0.9, lineCap: 'round', lineJoin: 'round' })
        ]).addTo(map);
        
        map.fitBounds(activeRoutePolyline.getBounds());
    })
    .catch(error => {
        findBtn.innerText = "FIND SAFE ROUTE";
        findBtn.disabled = false;
        alert(`Failed to find safe route: ${error.message}`);
    });
}

function startEvacuation() {
    if (!currentSelectedShelter) {
        alert("No recommended shelter selected. Please calculate a safe route first.");
        return;
    }
    
    const startBtn = document.getElementById('startEvacuationBtn');
    startBtn.innerText = "Starting Evacuation...";
    startBtn.disabled = true;
    
    fetch('/api/evacuation/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ shelter_id: currentSelectedShelter.id })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Server error'); });
        }
        return response.json();
    })
    .then(data => {
        startBtn.innerText = "START EVACUATION";
        startBtn.disabled = false;
        
        // Update current selected shelter capacity on UI
        currentSelectedShelter = data.shelter;
        document.getElementById('recCapacity').innerText = `${data.shelter.availableCapacity} / ${data.shelter.capacity}`;
        
        // Also update nearest shelters list to reflect capacity change
        if (currentCoords) {
            displayNearestShelters(currentCoords.latitude, currentCoords.longitude);
        }
        
        alert("Evacuation process started! Follow the glowing route on the map to seek safety.\n\n" + data.message);
    })
    .catch(error => {
        startBtn.innerText = "START EVACUATION";
        startBtn.disabled = false;
        alert(`Failed to start evacuation: ${error.message}`);
    });
}

function recalculateRoute() {
    if (!currentCoords) return;
    
    const recalcBtn = document.getElementById('recalculateRouteBtn');
    recalcBtn.innerText = "Recalculating...";
    recalcBtn.disabled = true;
    
    fetch('/api/routes/recalculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentCoords)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Server error'); });
        }
        return response.json();
    })
    .then(data => {
        recalcBtn.innerText = "RECALCULATE ROUTE";
        recalcBtn.disabled = false;
        
        // Save current shelter info
        currentSelectedShelter = data.shelter;
        
        // Update route details
        document.getElementById('recShelterName').innerText = `🏠 ${data.shelter.name}`;
        document.getElementById('recDistance').innerText = `${data.shelter.distance.toFixed(2)} km`;
        const durationMins = Math.round(data.route.duration / 60);
        document.getElementById('recTime').innerText = `${durationMins} mins`;
        
        const risk = data.shelter.riskLevel;
        const riskColor = getRiskColor(risk);
        document.getElementById('recRisk').innerHTML = `<span style="color: ${riskColor};">${risk}</span>`;
        
        const safetyScorePercent = Math.round(data.route.safetyScore * 100);
        document.getElementById('recSafety').innerText = `${safetyScorePercent}%`;
        document.getElementById('recCapacity').innerText = `${data.shelter.availableCapacity} / ${data.shelter.capacity}`;
        document.getElementById('recReason').innerText = `Reason: "${data.reason}"`;
        
        // Re-plot
        if (activeRoutePolyline) {
            map.removeLayer(activeRoutePolyline);
        }
        const coordinates = data.route.geometry.coordinates.map(coord => [coord[1], coord[0]]);
        activeRoutePolyline = L.featureGroup([
            L.polyline(coordinates, { color: '#1e3a8a', weight: 10, opacity: 0.5, lineCap: 'round', lineJoin: 'round' }),
            L.polyline(coordinates, { color: '#3b82f6', weight: 6, opacity: 0.9, lineCap: 'round', lineJoin: 'round' })
        ]).addTo(map);
        
        alert("Safer route recalculated successfully!");
    })
    .catch(error => {
        recalcBtn.innerText = "RECALCULATE ROUTE";
        recalcBtn.disabled = false;
        alert(`Recalculation failed: ${error.message}`);
    });
}
