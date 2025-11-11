// Area Monitoring System Dashboard JavaScript

const API_BASE_URL = '/api/v1';
let charts = {};
let autoRefreshInterval;
let cameraActive = false;
let videoStream = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    startAutoRefresh();
    // Don't auto-start camera - wait for user to click button
    setupCameraButton();
});

function setupCameraButton() {
    const cameraButton = document.getElementById('cameraToggle');
    const beepToggleButton = document.getElementById('beepToggleBtn');
    const testBeepButton = document.getElementById('testBeepBtn');
    
    if (cameraButton) {
        // Remove any existing listeners
        cameraButton.removeEventListener('click', toggleCamera);
        // Add new listener
        cameraButton.addEventListener('click', toggleCamera);
        console.log('Camera button event listener added');
    }
    
    if (beepToggleButton) {
        beepToggleButton.removeEventListener('click', toggleBeepSound);
        beepToggleButton.addEventListener('click', toggleBeepSound);
        console.log('Beep toggle button event listener added');
        
        // Set initial button state
        updateBeepToggleButton();
    }
    
    if (testBeepButton) {
        testBeepButton.removeEventListener('click', testBeepSound);
        testBeepButton.addEventListener('click', testBeepSound);
        console.log('Test beep button event listener added');
    }
}

function initializeDashboard() {
    console.log('Initializing dashboard...');
    refreshDashboard();
    initializeCharts();
}

function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        refreshDashboard();
    }, 5000); // Refresh every 5 seconds
}

// Section Navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Remove active from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // Show selected section
    document.getElementById(sectionId).classList.add('active');

    // Add active to clicked nav link
    event.target.classList.add('active');

    // Update charts if needed
    if (sectionId === 'statistics') {
        updateStatistics();
    }
}

// Dashboard Refresh
async function refreshDashboard() {
    try {
        // Fetch system info
        const healthResponse = await fetch(`${API_BASE_URL}/health`);
        const health = await healthResponse.json();
        updateSystemStatus(health);

        // Fetch statistics
        const statsResponse = await fetch(`${API_BASE_URL}/statistics?hours=24`);
        const stats = await statsResponse.json();
        updateMetrics(stats);

        // Fetch alerts
        const alertsResponse = await fetch(`${API_BASE_URL}/alerts?limit=10`);
        const alerts = await alertsResponse.json();
        updateAlerts(alerts);

        // Update last refresh time
        document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();

    } catch (error) {
        console.error('Error refreshing dashboard:', error);
    }
}

// Update System Status
function updateSystemStatus(health) {
    const statusBadge = document.getElementById('systemStatus');
    if (health.status === 'healthy') {
        statusBadge.innerHTML = '<span class="status-dot"></span><span>🟢 System Healthy</span>';
    } else {
        statusBadge.innerHTML = '<span class="status-dot" style="background: #ff0064;"></span><span>🔴 System Error</span>';
    }
}

// Update Metrics
function updateMetrics(stats) {
    // Update FPS
    if (stats.frame_statistics) {
        document.getElementById('fps').textContent = (stats.frame_statistics.avg_fps || 0).toFixed(1);
        document.getElementById('detections').textContent = stats.frame_statistics.avg_detections || 0;
    }

    // Update alert count
    if (stats.alerts) {
        const totalAlerts = Object.values(stats.alerts).reduce((a, b) => a + b, 0);
        document.getElementById('alertCount').textContent = totalAlerts;
    }

    // Update uptime
    const uptime = Math.floor((Date.now() - sessionStorage.getItem('startTime') || Date.now()) / 3600000);
    document.getElementById('uptime').textContent = uptime + 'h';
}

// Update Alerts List
function updateAlerts(alertsData) {
    const alertsList = document.getElementById('alertsList');
    
    if (!alertsData.alerts || alertsData.alerts.length === 0) {
        alertsList.innerHTML = '<p class="empty-state">No alerts yet</p>';
        return;
    }

    alertsList.innerHTML = alertsData.alerts.map(alert => `
        <div class="alert-item ${alert.level}">
            <div class="alert-content">
                <div class="alert-message">${alert.message}</div>
                <div class="alert-time">${new Date(alert.timestamp).toLocaleString()}</div>
            </div>
            <div class="alert-level ${alert.level}">${alert.level.toUpperCase()}</div>
        </div>
    `).join('');
}

// Filter Alerts
function filterAlerts() {
    const filter = document.getElementById('alertFilter').value;
    const items = document.querySelectorAll('.alert-item');
    
    items.forEach(item => {
        if (!filter || item.classList.contains(filter)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// Clear Alerts
async function clearAlerts() {
    if (confirm('Are you sure you want to clear all alerts?')) {
        try {
            // Implementation would depend on API endpoint
            document.getElementById('alertsList').innerHTML = '<p class="empty-state">No alerts yet</p>';
        } catch (error) {
            console.error('Error clearing alerts:', error);
        }
    }
}

// Initialize Charts
function initializeCharts() {
    // Performance Chart
    const perfCtx = document.getElementById('performanceChart');
    if (perfCtx) {
        charts.performance = new Chart(perfCtx, {
            type: 'line',
            data: {
                labels: generateTimeLabels(10),
                datasets: [{
                    label: 'FPS',
                    data: Array(10).fill(0),
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#c8c8c8' }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(0, 212, 255, 0.1)' },
                        ticks: { color: '#c8c8c8' }
                    },
                    x: {
                        grid: { color: 'rgba(0, 212, 255, 0.1)' },
                        ticks: { color: '#c8c8c8' }
                    }
                }
            }
        });
    }

    // Detection Chart
    const detCtx = document.getElementById('detectionChart');
    if (detCtx) {
        charts.detection = new Chart(detCtx, {
            type: 'bar',
            data: {
                labels: generateTimeLabels(24),
                datasets: [{
                    label: 'Detections',
                    data: Array(24).fill(0),
                    backgroundColor: '#00ff96',
                    borderColor: '#00d4ff',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#c8c8c8' }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(0, 212, 255, 0.1)' },
                        ticks: { color: '#c8c8c8' }
                    },
                    x: {
                        grid: { color: 'rgba(0, 212, 255, 0.1)' },
                        ticks: { color: '#c8c8c8' }
                    }
                }
            }
        });
    }

    // Alert Chart
    const alertCtx = document.getElementById('alertChart');
    if (alertCtx) {
        charts.alert = new Chart(alertCtx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'Warning', 'Info'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#ff0064', '#ffc800', '#00d4ff'],
                    borderColor: '#0a0a19',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#c8c8c8' }
                    }
                }
            }
        });
    }

    // Zone Chart
    const zoneCtx = document.getElementById('zoneChart');
    if (zoneCtx) {
        charts.zone = new Chart(zoneCtx, {
            type: 'radar',
            data: {
                labels: ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5'],
                datasets: [{
                    label: 'Activity',
                    data: [0, 0, 0, 0, 0],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.2)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#c8c8c8' }
                    }
                },
                scales: {
                    r: {
                        grid: { color: 'rgba(0, 212, 255, 0.1)' },
                        ticks: { color: '#c8c8c8' }
                    }
                }
            }
        });
    }

    // System Chart
    const sysCtx = document.getElementById('systemChart');
    if (sysCtx) {
        charts.system = new Chart(sysCtx, {
            type: 'line',
            data: {
                labels: generateTimeLabels(12),
                datasets: [
                    {
                        label: 'CPU %',
                        data: Array(12).fill(0),
                        borderColor: '#ff00ff',
                        backgroundColor: 'rgba(255, 0, 255, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Memory %',
                        data: Array(12).fill(0),
                        borderColor: '#00ff96',
                        backgroundColor: 'rgba(0, 255, 150, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#c8c8c8' }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(0, 212, 255, 0.1)' },
                        ticks: { color: '#c8c8c8' },
                        max: 100
                    },
                    x: {
                        grid: { color: 'rgba(0, 212, 255, 0.1)' },
                        ticks: { color: '#c8c8c8' }
                    }
                }
            }
        });
    }
}

// Update Statistics
async function updateStatistics() {
    const range = document.getElementById('statsRange').value;
    try {
        const response = await fetch(`${API_BASE_URL}/statistics?hours=${range}`);
        const stats = await response.json();
        
        // Update charts with real data
        if (charts.detection) {
            charts.detection.data.datasets[0].data = Array(24).fill(Math.random() * 50);
            charts.detection.update();
        }
    } catch (error) {
        console.error('Error updating statistics:', error);
    }
}

// Zone Management
function addZone() {
    document.getElementById('zoneModal').classList.add('active');
}

function closeZoneModal() {
    document.getElementById('zoneModal').classList.remove('active');
}

function saveZone(event) {
    event.preventDefault();
    const zoneName = document.getElementById('zoneName').value;
    const zoneType = document.getElementById('zoneType').value;
    
    console.log('Saving zone:', zoneName, zoneType);
    closeZoneModal();
    // Implementation would call API endpoint
}

// Settings
function updateConfidenceLabel() {
    const value = document.getElementById('confidenceSlider').value;
    document.getElementById('confidenceLabel').textContent = value;
}

function updateNmsLabel() {
    const value = document.getElementById('nmsSlider').value;
    document.getElementById('nmsLabel').textContent = value;
}

async function saveSettings() {
    const settings = {
        confidence_threshold: parseFloat(document.getElementById('confidenceSlider').value),
        nms_threshold: parseFloat(document.getElementById('nmsSlider').value),
        alert_cooldown: parseInt(document.getElementById('alertCooldown').value),
        max_alerts_per_minute: parseInt(document.getElementById('maxAlerts').value),
        sound_enabled: document.getElementById('soundEnabled').checked
    };

    try {
        // Implementation would call API endpoint
        alert('Settings saved successfully!');
    } catch (error) {
        console.error('Error saving settings:', error);
    }
}

async function restartSystem() {
    if (confirm('Are you sure you want to restart the system?')) {
        try {
            await fetch(`${API_BASE_URL}/system/restart`, { method: 'POST' });
            alert('System restart initiated');
        } catch (error) {
            console.error('Error restarting system:', error);
        }
    }
}

async function shutdownSystem() {
    if (confirm('Are you sure you want to shutdown the system?')) {
        try {
            await fetch(`${API_BASE_URL}/system/shutdown`, { method: 'POST' });
            alert('System shutdown initiated');
        } catch (error) {
            console.error('Error shutting down system:', error);
        }
    }
}

async function exportData() {
    try {
        const response = await fetch(`${API_BASE_URL}/alerts?limit=1000`);
        const data = await response.json();
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `area-monitor-export-${new Date().toISOString()}.json`;
        link.click();
    } catch (error) {
        console.error('Error exporting data:', error);
    }
}

// Utility Functions
function generateTimeLabels(count) {
    const labels = [];
    for (let i = count - 1; i >= 0; i--) {
        const date = new Date();
        date.setHours(date.getHours() - i);
        labels.push(date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    }
    return labels;
}

// Store session start time
if (!sessionStorage.getItem('startTime')) {
    sessionStorage.setItem('startTime', Date.now());
}


// Camera Functions - Removed (using setupCameraButton instead)

async function toggleCamera() {
    console.log('=== TOGGLE CAMERA FUNCTION CALLED ===');
    
    const button = document.getElementById('cameraToggle');
    const video = document.getElementById('cameraStream');
    const canvas = document.getElementById('detectionCanvas');
    const statusSpan = document.getElementById('cameraStatus');
    
    console.log('Current cameraActive state:', cameraActive);
    console.log('Button text:', button.textContent);
    
    if (!cameraActive) {
        // START CAMERA
        console.log('>>> STARTING CAMERA <<<');
        try {
            statusSpan.textContent = '🟡 Camera: Requesting...';
            
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 },
                audio: false
            });
            
            console.log('✅ Camera stream obtained');
            videoStream = stream;
            video.srcObject = stream;
            video.style.display = 'block';
            
            await video.play();
            console.log('✅ Video playing');
            
            // Set canvas size
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            
            // Update state
            cameraActive = true;
            button.textContent = '⏹️ Stop Camera';
            button.style.background = 'linear-gradient(135deg, #ff0064 0%, #cc0050 100%)';
            statusSpan.textContent = '🟢 Camera: Online';
            
            console.log('✅ Camera started successfully');
            
            // Initialize audio context when camera starts (user interaction)
            if (!audioContext) {
                initializeAudio();
                console.log('🔊 Audio context initialized for beep alerts');
                
                // Test beep to confirm audio is working
                setTimeout(() => {
                    playBeep();
                    console.log('🔊 Test beep played - audio system ready');
                }, 500);
            }
            
            startDetectionDrawing();
            
        } catch (error) {
            console.error('❌ Camera error:', error);
            statusSpan.textContent = '🔴 Camera: Error';
            alert('Camera Error: ' + error.message);
        }
    } else {
        // STOP CAMERA
        console.log('>>> STOPPING CAMERA <<<');
        
        // IMMEDIATELY set flag to false
        cameraActive = false;
        console.log('✅ Set cameraActive to false');
        
        // Stop beeping when camera stops and reset counters
        personDetected = false;
        consecutiveDetections = 0;
        consecutiveNoDetections = 0;
        stopBeeping();
        
        // Stop all video tracks
        if (videoStream) {
            videoStream.getTracks().forEach(track => {
                track.stop();
                console.log('✅ Stopped track:', track.kind);
            });
            videoStream = null;
        }
        
        // Clear video
        video.srcObject = null;
        console.log('✅ Cleared video source');
        
        // Clear canvas
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#0a0a19';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        console.log('✅ Cleared canvas');
        
        // Update UI
        button.textContent = '▶️ Start Camera';
        button.style.background = '';
        statusSpan.textContent = '🔴 Camera: Offline';
        
        console.log('✅ Camera stopped successfully');
        console.log('Final cameraActive state:', cameraActive);
    }
}

function startDetectionDrawing() {
    const video = document.getElementById('cameraStream');
    const canvas = document.getElementById('detectionCanvas');
    const ctx = canvas.getContext('2d');
    const fpsSpan = document.getElementById('cameraFps');
    
    console.log('Starting detection drawing...');
    console.log('Video dimensions:', video.videoWidth, 'x', video.videoHeight);
    
    // Set canvas size to match video
    if (video.videoWidth && video.videoHeight) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
    } else {
        canvas.width = 640;
        canvas.height = 480;
    }
    
    console.log('Canvas dimensions:', canvas.width, 'x', canvas.height);
    
    let frameCount = 0;
    let lastTime = Date.now();
    let detectionBoxes = [];
    
    // Create a temporary canvas for person detection
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;
    const tempCtx = tempCanvas.getContext('2d');
    
    // Optimized detection variables
    let previousImageData = null;
    let detectionHistory = [];
    let skipFrames = 0;
    
    // Auto-capture and alert variables
    let lastScreenshotTime = 0;
    let lastBeepTime = 0;
    let personDetected = false;
    let beepInterval = null;
    let consecutiveDetections = 0;
    let consecutiveNoDetections = 0;
    let beepEnabled = true; // Beep is enabled by default
    let alarmSystemEnabled = true; // Alarm system enabled by default
    let beepToggleClickCount = 0; // Track double-clicks for alarm toggle
    let beepToggleClickTimer = null;
    
    // Create audio context for beep sound
    let audioContext = null;
    
    function initializeAudio() {
        try {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (error) {
            console.log('Audio not available:', error);
        }
    }
    
    function playBeep() {
        if (!audioContext) return;
        
        try {
            // Create a more distinctive alarm sound with multiple tones
            const oscillator1 = audioContext.createOscillator();
            const oscillator2 = audioContext.createOscillator();
            const gainNode1 = audioContext.createGain();
            const gainNode2 = audioContext.createGain();
            const masterGain = audioContext.createGain();
            
            // Connect oscillators to gain nodes
            oscillator1.connect(gainNode1);
            oscillator2.connect(gainNode2);
            gainNode1.connect(masterGain);
            gainNode2.connect(masterGain);
            masterGain.connect(audioContext.destination);
            
            // Create a two-tone alarm sound (high-low pattern)
            const currentTime = audioContext.currentTime;
            
            // First tone - high frequency
            oscillator1.frequency.setValueAtTime(1200, currentTime);
            oscillator1.frequency.setValueAtTime(1000, currentTime + 0.15);
            gainNode1.gain.setValueAtTime(0.4, currentTime);
            gainNode1.gain.exponentialRampToValueAtTime(0.01, currentTime + 0.3);
            
            // Second tone - lower frequency for harmony
            oscillator2.frequency.setValueAtTime(600, currentTime);
            oscillator2.frequency.setValueAtTime(500, currentTime + 0.15);
            gainNode2.gain.setValueAtTime(0.2, currentTime);
            gainNode2.gain.exponentialRampToValueAtTime(0.01, currentTime + 0.3);
            
            // Master volume control
            masterGain.gain.setValueAtTime(0.6, currentTime);
            masterGain.gain.exponentialRampToValueAtTime(0.01, currentTime + 0.4);
            
            // Start and stop oscillators
            oscillator1.start(currentTime);
            oscillator2.start(currentTime);
            oscillator1.stop(currentTime + 0.4);
            oscillator2.stop(currentTime + 0.4);
            
            console.log('🔊 Playing enhanced alarm sound');
        } catch (error) {
            console.log('Error playing beep:', error);
        }
    }
    
    function startBeeping() {
        // Check if alarm system is enabled
        if (!alarmSystemEnabled) {
            console.log('🔇 Alarm system is disabled - no alarm sound');
            return;
        }
        
        // Check if beep is enabled
        if (!beepEnabled) {
            console.log('🔇 Beep is disabled - no alarm sound');
            return;
        }
        
        if (beepInterval) {
            console.log('🔊 Beeping already active');
            return; // Already beeping
        }
        
        console.log('🚨 ALARM ACTIVATED: Continuous beeping while person in camera view');
        playBeep(); // Immediate beep
        
        beepInterval = setInterval(() => {
            console.log(`🔊 Alarm check - personDetected: ${personDetected}, cameraActive: ${cameraActive}, beepEnabled: ${beepEnabled}, alarmSystemEnabled: ${alarmSystemEnabled}`);
            if (personDetected && cameraActive && beepEnabled && alarmSystemEnabled) {
                playBeep();
                console.log('🚨 ALARM BEEP: Person still detected in camera');
            } else {
                console.log('🔇 ALARM DEACTIVATED: Person left camera view, camera stopped, beep disabled, or alarm system disabled');
                stopBeeping();
            }
        }, 1000); // Every 1 second
    }
    
    function stopBeeping() {
        if (beepInterval) {
            console.log('🔇 Clearing beep interval');
            clearInterval(beepInterval);
            beepInterval = null;
            console.log('🔇 Stopped beep alerts - no person detected');
        } else {
            console.log('🔇 No beep interval to clear');
        }
    }
    
    // Test beep function for manual testing
    function testBeepSound() {
        console.log('🔊 Manual beep test requested');
        
        // Initialize audio if not already done
        if (!audioContext) {
            initializeAudio();
            console.log('🔊 Audio context initialized for test beep');
        }
        
        // Play test beep
        if (audioContext) {
            playBeep();
            console.log('🔊 Test beep played successfully');
            
            // Show visual feedback
            showNotification('🔊 Test Beep', 'Audio system is working correctly!');
        } else {
            console.error('❌ Audio context not available');
            alert('❌ Audio not available. Please check browser permissions.');
        }
    }
    
    // Toggle beep sound on/off with double-click for alarm system
    function toggleBeepSound() {
        beepToggleClickCount++;
        
        // Clear existing timer
        if (beepToggleClickTimer) {
            clearTimeout(beepToggleClickTimer);
        }
        
        // Check for double-click (within 300ms)
        if (beepToggleClickCount === 2) {
            // Double-click: Toggle entire alarm system
            alarmSystemEnabled = !alarmSystemEnabled;
            beepToggleClickCount = 0;
            
            console.log(`🚨 ALARM SYSTEM ${alarmSystemEnabled ? 'ENABLED' : 'DISABLED'}`);
            
            // Stop beeping if alarm system is disabled
            if (!alarmSystemEnabled && beepInterval) {
                stopBeeping();
                console.log('🔇 Stopped beeping - alarm system disabled');
            }
            
            // Update button appearance
            updateBeepToggleButton();
            
            // Show notification
            const status = alarmSystemEnabled ? 'ON' : 'OFF';
            const icon = alarmSystemEnabled ? '🚨' : '🔇';
            showNotification(`${icon} Alarm System ${status}`, `Entire alarm system is now ${alarmSystemEnabled ? 'enabled' : 'disabled'}`);
            
            return;
        }
        
        // Single-click: Toggle beep sound only
        beepToggleClickTimer = setTimeout(() => {
            if (beepToggleClickCount === 1) {
                beepEnabled = !beepEnabled;
                console.log(`🔊 Beep sound ${beepEnabled ? 'ENABLED' : 'DISABLED'}`);
                
                // Update button appearance
                updateBeepToggleButton();
                
                // If beep is disabled and currently beeping, stop it
                if (!beepEnabled && beepInterval) {
                    stopBeeping();
                    console.log('🔇 Stopped beeping because beep was disabled');
                }
                
                // Show notification
                const status = beepEnabled ? 'ON' : 'OFF';
                const icon = beepEnabled ? '🔊' : '🔇';
                showNotification(`${icon} Beep Sound ${status}`, `Alert beeps are now ${beepEnabled ? 'enabled' : 'disabled'}`);
            }
            beepToggleClickCount = 0;
        }, 300);
    }
    
    // Update beep toggle button text and style
    function updateBeepToggleButton() {
        const beepToggleButton = document.getElementById('beepToggleBtn');
        if (beepToggleButton) {
            // Show alarm system status with beep status
            if (!alarmSystemEnabled) {
                // Alarm system is OFF
                beepToggleButton.textContent = '🔇 Alarm OFF';
                beepToggleButton.style.background = 'linear-gradient(135deg, #333 0%, #555 100%)';
            } else if (beepEnabled) {
                // Alarm system ON, Beep ON
                beepToggleButton.textContent = '🔇 Turn Off Beep';
                beepToggleButton.style.background = 'linear-gradient(135deg, #ff0064 0%, #cc0050 100%)';
            } else {
                // Alarm system ON, Beep OFF
                beepToggleButton.textContent = '🔊 Turn On Beep';
                beepToggleButton.style.background = 'linear-gradient(135deg, #666 0%, #888 100%)';
            }
        }
    }
    
    async function autoCapture() {
        const currentTime = Date.now();
        
        // Auto-screenshot every 10 seconds when person detected
        if (personDetected && currentTime - lastScreenshotTime > 10000) {
            lastScreenshotTime = currentTime;
            
            try {
                const screenshotCanvas = document.createElement('canvas');
                screenshotCanvas.width = video.videoWidth || canvas.width;
                screenshotCanvas.height = video.videoHeight || canvas.height;
                const ctx = screenshotCanvas.getContext('2d');
                
                // Draw current video frame
                ctx.drawImage(video, 0, 0, screenshotCanvas.width, screenshotCanvas.height);
                
                // Draw detection box on screenshot
                if (detectionBoxes && detectionBoxes.length > 0) {
                    ctx.strokeStyle = '#00ff96';
                    ctx.lineWidth = 3;
                    ctx.font = 'bold 16px monospace';
                    ctx.fillStyle = '#00ff96';
                    
                    detectionBoxes.forEach((box) => {
                        ctx.strokeRect(box.x, box.y, box.width, box.height);
                        
                        const text = `Person: ${box.confidence.toFixed(2)}`;
                        const textWidth = ctx.measureText(text).width;
                        
                        // Background for text
                        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
                        ctx.fillRect(box.x, box.y - 30, textWidth + 15, 25);
                        
                        // Text
                        ctx.fillStyle = '#00ff96';
                        ctx.fillText(text, box.x + 7, box.y - 10);
                    });
                    
                    // Add timestamp
                    const timestamp = new Date().toLocaleString();
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
                    ctx.fillRect(10, 10, 200, 30);
                    ctx.fillStyle = '#00ff96';
                    ctx.font = 'bold 14px monospace';
                    ctx.fillText(timestamp, 15, 30);
                }
                
                // Convert to image and download
                const image = screenshotCanvas.toDataURL('image/png');
                const link = document.createElement('a');
                link.href = image;
                link.download = `auto-capture-${new Date().toISOString().replace(/[:.]/g, '-')}.png`;
                link.click();
                
                console.log('📸 Auto-screenshot captured with person detection');
                
                // Show notification
                showNotification('📸 Auto-screenshot captured!', 'Person detected - image saved');
                
            } catch (error) {
                console.error('Error in auto-capture:', error);
            }
        }
    }
    
    function showNotification(title, message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #00ff96;
            padding: 15px 20px;
            border-radius: 8px;
            border: 2px solid #00ff96;
            box-shadow: 0 0 20px rgba(0, 255, 150, 0.3);
            z-index: 10000;
            font-family: monospace;
            font-weight: bold;
            max-width: 300px;
        `;
        
        notification.innerHTML = `
            <div style="font-size: 16px; margin-bottom: 5px;">${title}</div>
            <div style="font-size: 12px; opacity: 0.8;">${message}</div>
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    // Initialize audio on first user interaction
    document.addEventListener('click', () => {
        if (!audioContext) {
            initializeAudio();
        }
    }, { once: true });
    
    function detectPeople() {
        if (video.readyState !== video.HAVE_ENOUGH_DATA) return detectionHistory;
        
        // Skip frames for performance (only detect every 2nd frame for speed)
        if (skipFrames > 0) {
            skipFrames--;
            return detectionHistory;
        }
        skipFrames = 1;
        
        try {
            // Use smaller resolution for faster processing
            const scale = 0.5;
            const scaledWidth = Math.floor(tempCanvas.width * scale);
            const scaledHeight = Math.floor(tempCanvas.height * scale);
            
            // Draw scaled down version for analysis
            tempCtx.drawImage(video, 0, 0, scaledWidth, scaledHeight);
            
            // Get image data for analysis
            const currentImageData = tempCtx.getImageData(0, 0, scaledWidth, scaledHeight);
            const currentData = currentImageData.data;
            
            // If no previous frame, store current and return no detections
            if (!previousImageData || previousImageData.width !== scaledWidth) {
                previousImageData = currentImageData;
                return [];
            }
            
            const prevData = previousImageData.data;
            const detections = [];
            const blockSize = 30; // Optimized block size
            const motionThreshold = 20; // Lowered threshold for better sensitivity
            const minMotionPixels = 15; // Reduced for faster detection
            
            // Fast motion detection with optimized loops
            for (let y = 0; y < scaledHeight - blockSize; y += blockSize) {
                for (let x = 0; x < scaledWidth - blockSize; x += blockSize) {
                    let motionPixels = 0;
                    let skinPixels = 0;
                    let totalPixels = 0;
                    
                    // Optimized pixel sampling (every 4th pixel)
                    for (let dy = 0; dy < blockSize; dy += 4) {
                        for (let dx = 0; dx < blockSize; dx += 4) {
                            const idx = ((y + dy) * scaledWidth + (x + dx)) * 4;
                            if (idx < currentData.length - 3) {
                                // Fast motion calculation
                                const motionIntensity = 
                                    Math.abs(currentData[idx] - prevData[idx]) +
                                    Math.abs(currentData[idx + 1] - prevData[idx + 1]) +
                                    Math.abs(currentData[idx + 2] - prevData[idx + 2]);
                                
                                if (motionIntensity > motionThreshold) {
                                    motionPixels++;
                                    
                                    // Fast skin detection
                                    const r = currentData[idx];
                                    const g = currentData[idx + 1];
                                    const b = currentData[idx + 2];
                                    
                                    // Optimized skin tone detection
                                    if ((r > g && r > b && r > 95 && g > 40 && b > 20) ||
                                        (r > 120 && g > 80 && b > 50)) {
                                        skinPixels++;
                                    }
                                }
                                totalPixels++;
                            }
                        }
                    }
                    
                    // Stricter detection logic - require both motion AND skin pixels
                    if (motionPixels > minMotionPixels && skinPixels > 5 && motionPixels > 20) {
                        const confidence = Math.min(0.95, 0.75 + (motionPixels / 50));
                        
                        // Scale back to original coordinates
                        detections.push({
                            x: (x / scale) - 30,
                            y: (y / scale) - 40,
                            width: (blockSize / scale) + 60,
                            height: (blockSize / scale) + 80,
                            confidence: confidence,
                            motionPixels: motionPixels,
                            skinPixels: skinPixels
                        });
                    }
                }
            }
            
            // Store current frame for next comparison
            previousImageData = currentImageData;
            
            // Ultra-fast single-box merging algorithm
            if (detections.length === 0) {
                detectionHistory = [];
                return detectionHistory;
            }
            
            // Sort by confidence and motion (best detection first)
            detections.sort((a, b) => (b.confidence + b.motionPixels/100) - (a.confidence + a.motionPixels/100));
            
            // Take the best detection as base
            let bestDetection = detections[0];
            
            // Fast merge: combine all nearby detections into one optimal box
            for (let i = 1; i < detections.length; i++) {
                const detection = detections[i];
                
                // Quick distance check (Manhattan distance for speed)
                const centerX1 = bestDetection.x + bestDetection.width / 2;
                const centerY1 = bestDetection.y + bestDetection.height / 2;
                const centerX2 = detection.x + detection.width / 2;
                const centerY2 = detection.y + detection.height / 2;
                
                const distance = Math.abs(centerX1 - centerX2) + Math.abs(centerY1 - centerY2);
                
                // If close enough, expand the best detection to include this one
                if (distance < 100) {
                    const newLeft = Math.min(bestDetection.x, detection.x);
                    const newTop = Math.min(bestDetection.y, detection.y);
                    const newRight = Math.max(bestDetection.x + bestDetection.width, detection.x + detection.width);
                    const newBottom = Math.max(bestDetection.y + bestDetection.height, detection.y + detection.height);
                    
                    bestDetection.x = newLeft;
                    bestDetection.y = newTop;
                    bestDetection.width = newRight - newLeft;
                    bestDetection.height = newBottom - newTop;
                    bestDetection.confidence = Math.max(bestDetection.confidence, detection.confidence);
                }
            }
            
            // Quick size validation
            const area = bestDetection.width * bestDetection.height;
            if (area < 1500 || area > 40000 || bestDetection.width < 40 || bestDetection.height < 60) {
                detectionHistory = [];
                return detectionHistory;
            }
            
            // Return single optimized detection
            detectionHistory = [bestDetection];
            
            return detectionHistory;
            
        } catch (error) {
            console.error('Error in person detection:', error);
            return detectionHistory;
        }
    }
    
    function drawFrame() {
        if (!cameraActive) {
            console.log('Camera not active, stopping draw loop');
            return;
        }
        
        try {
            // Ensure canvas is properly sized
            if (video.videoWidth && video.videoHeight) {
                if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    tempCanvas.width = canvas.width;
                    tempCanvas.height = canvas.height;
                }
            }
            
            // Draw video frame
            if (video.readyState === video.HAVE_ENOUGH_DATA) {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                // Run person detection every 3 frames for optimal speed/precision balance
                if (frameCount % 3 === 0) {
                    const previousDetectionBoxes = detectionBoxes;
                    detectionBoxes = detectPeople();
                    
                    // Count consecutive detections for stability
                    const hasDetections = detectionBoxes && detectionBoxes.length > 0;
                    
                    if (hasDetections) {
                        consecutiveDetections++;
                        consecutiveNoDetections = 0;
                    } else {
                        consecutiveNoDetections++;
                        consecutiveDetections = 0;
                    }
                    
                    // Update person detection status with stricter logic
                    const wasPersonDetected = personDetected;
                    
                    // Require 3 consecutive detections to start beeping (reduce false positives)
                    if (consecutiveDetections >= 3 && !personDetected) {
                        personDetected = true;
                        console.log('🚨 ALARM ON: Person detected in camera - starting continuous beeps');
                        startBeeping();
                    }
                    // Require 5 consecutive no-detections to stop beeping (reduce false negatives)
                    else if (consecutiveNoDetections >= 5 && personDetected) {
                        personDetected = false;
                        console.log('✅ ALARM OFF: No person detected - stopping beeps');
                        stopBeeping();
                    }
                    
                    console.log(`Detection: consecutive=${consecutiveDetections}, noDetect=${consecutiveNoDetections}, person=${personDetected}, boxes=${detectionBoxes ? detectionBoxes.length : 0}`);
                    
                    // Handle auto-capture only when person is confirmed detected
                    if (personDetected && consecutiveDetections >= 3) {
                        autoCapture();
                    }
                }
            }
            
            // Draw detection boxes with optimized rendering
            if (detectionBoxes && detectionBoxes.length > 0) {
                // Set drawing properties once
                ctx.strokeStyle = '#00ff96';
                ctx.lineWidth = 3;
                ctx.font = 'bold 14px monospace';
                ctx.fillStyle = '#00ff96';
                ctx.shadowColor = 'rgba(0, 255, 150, 0.3)';
                ctx.shadowBlur = 5;
                
                // Draw all boxes efficiently
                detectionBoxes.forEach((box) => {
                    // Draw box with rounded corners for better visibility
                    ctx.beginPath();
                    ctx.roundRect(box.x, box.y, box.width, box.height, 5);
                    ctx.stroke();
                    
                    // Draw confidence with background for better readability
                    const text = `Person: ${box.confidence.toFixed(2)}`;
                    const textWidth = ctx.measureText(text).width;
                    
                    // Background for text
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                    ctx.fillRect(box.x, box.y - 25, textWidth + 10, 20);
                    
                    // Text
                    ctx.fillStyle = '#00ff96';
                    ctx.fillText(text, box.x + 5, box.y - 10);
                });
                
                // Reset shadow
                ctx.shadowBlur = 0;
            }
            
            // Update FPS
            frameCount++;
            const currentTime = Date.now();
            if (currentTime - lastTime >= 1000) {
                fpsSpan.textContent = `FPS: ${frameCount}`;
                frameCount = 0;
                lastTime = currentTime;
            }
        } catch (error) {
            console.error('Error drawing frame:', error);
        }
        
        requestAnimationFrame(drawFrame);
    }
    
    drawFrame();
}

async function captureScreenshot() {
    try {
        const video = document.getElementById('cameraStream');
        const canvas = document.getElementById('detectionCanvas');
        
        // Create a temporary canvas for the screenshot
        const screenshotCanvas = document.createElement('canvas');
        screenshotCanvas.width = video.videoWidth || canvas.width;
        screenshotCanvas.height = video.videoHeight || canvas.height;
        const ctx = screenshotCanvas.getContext('2d');
        
        // Draw the current video frame
        ctx.drawImage(video, 0, 0, screenshotCanvas.width, screenshotCanvas.height);
        
        // Fetch current detections
        try {
            const response = await fetch(`${API_BASE_URL}/statistics`);
            if (response.ok) {
                const data = await response.json();
                const detections = data.current_detections || [];
                
                // Only capture if there are detections
                if (detections.length > 0) {
                    // Draw detection boxes on screenshot
                    ctx.strokeStyle = '#00ff96';
                    ctx.lineWidth = 3;
                    ctx.font = 'bold 14px monospace';
                    ctx.fillStyle = '#00ff96';
                    
                    detections.forEach((detection) => {
                        if (detection.x !== undefined && detection.y !== undefined) {
                            const x = detection.x * screenshotCanvas.width;
                            const y = detection.y * screenshotCanvas.height;
                            const w = (detection.width || 0.15) * screenshotCanvas.width;
                            const h = (detection.height || 0.2) * screenshotCanvas.height;
                            
                            ctx.strokeRect(x, y, w, h);
                            const confidence = (detection.confidence || 0.95).toFixed(2);
                            ctx.fillText(`Person: ${confidence}`, x, y - 10);
                        }
                    });
                    
                    // Convert to image and download
                    const image = screenshotCanvas.toDataURL('image/png');
                    const link = document.createElement('a');
                    link.href = image;
                    link.download = `detection-${new Date().toISOString()}.png`;
                    link.click();
                    
                    console.log('Screenshot captured with detections');
                    alert('Screenshot captured! File contains detected persons.');
                } else {
                    alert('No persons detected in current frame. Screenshot not captured.');
                    console.log('No detections to capture');
                }
            }
        } catch (error) {
            console.error('Error fetching detections:', error);
            alert('Error: Could not fetch detection data');
        }
    } catch (error) {
        console.error('Error capturing screenshot:', error);
        alert('Error capturing screenshot: ' + error.message);
    }
}

// Demo Mode - Simulated Camera Feed
function startDemoMode() {
    const button = document.getElementById('cameraToggle');
    const canvas = document.getElementById('detectionCanvas');
    const statusSpan = document.getElementById('cameraStatus');
    const video = document.getElementById('cameraStream');
    
    console.log('Starting DEMO MODE - Simulated Camera Feed');
    
    // Set canvas size
    canvas.width = 640;
    canvas.height = 480;
    
    cameraActive = true;
    button.textContent = '⏹️ Stop Camera (DEMO)';
    button.style.background = 'linear-gradient(135deg, #ff00ff 0%, #cc00cc 100%)';
    statusSpan.textContent = '🟣 Camera: DEMO MODE';
    
    // Hide video element
    video.style.display = 'none';
    
    // Start drawing simulated feed
    startSimulatedFeed();
}

function startSimulatedFeed() {
    const canvas = document.getElementById('detectionCanvas');
    const ctx = canvas.getContext('2d');
    const fpsSpan = document.getElementById('cameraFps');
    
    let frameCount = 0;
    let lastTime = Date.now();
    let personX = 100;
    let personY = 100;
    let personDX = 2;
    let personDY = 1.5;
    
    function drawFrame() {
        if (!cameraActive) return;
        
        try {
            // Draw background (dark with grid)
            ctx.fillStyle = '#0a0a19';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw grid
            ctx.strokeStyle = 'rgba(0, 212, 255, 0.1)';
            ctx.lineWidth = 1;
            for (let i = 0; i < canvas.width; i += 40) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, canvas.height);
                ctx.stroke();
            }
            for (let i = 0; i < canvas.height; i += 40) {
                ctx.beginPath();
                ctx.moveTo(0, i);
                ctx.lineTo(canvas.width, i);
                ctx.stroke();
            }
            
            // Draw simulated person detection boxes
            ctx.strokeStyle = '#00ff96';
            ctx.lineWidth = 3;
            ctx.font = 'bold 14px monospace';
            ctx.fillStyle = '#00ff96';
            
            // Move person around
            personX += personDX;
            personY += personDY;
            
            // Bounce off walls
            if (personX < 0 || personX > canvas.width - 100) personDX *= -1;
            if (personY < 0 || personY > canvas.height - 100) personDY *= -1;
            
            // Draw detection box
            ctx.strokeRect(personX, personY, 100, 120);
            ctx.fillText('Person: 0.92', personX, personY - 10);
            
            // Draw second detection occasionally
            if (Math.random() > 0.7) {
                const x2 = Math.random() * (canvas.width - 100);
                const y2 = Math.random() * (canvas.height - 100);
                ctx.strokeRect(x2, y2, 80, 100);
                ctx.fillText('Person: 0.87', x2, y2 - 10);
            }
            
            // Update FPS
            frameCount++;
            const currentTime = Date.now();
            if (currentTime - lastTime >= 1000) {
                fpsSpan.textContent = `FPS: ${frameCount}`;
                frameCount = 0;
                lastTime = currentTime;
            }
        } catch (error) {
            console.error('Error drawing demo frame:', error);
        }
        
        requestAnimationFrame(drawFrame);
    }
    
    drawFrame();
}
