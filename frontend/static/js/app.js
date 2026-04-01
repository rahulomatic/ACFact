// Autonomous Content Factory - Frontend JavaScript

const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const contentForm = document.getElementById('contentForm');
const sourceTypeInputs = document.querySelectorAll('input[name="sourceType"]');
const textInputSection = document.getElementById('textInput');
const urlInputSection = document.getElementById('urlInput');
const fileInputSection = document.getElementById('fileInput');
const agentLogsContainer = document.getElementById('agentLogs');
const outputContentContainer = document.getElementById('outputContent');
const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
const loadExampleBtn = document.getElementById('loadExampleBtn');
const statsCard = document.getElementById('statsCard');

// Example data
const exampleContent = `Product: SmartWatch Pro X

Description:
The SmartWatch Pro X is a cutting-edge wearable device designed for fitness enthusiasts and health-conscious individuals who want to track their wellness journey with precision.

Key Features:
- Advanced heart rate monitoring with 24/7 continuous tracking
- Built-in GPS for accurate distance and route tracking
- 7-day battery life on a single charge
- Water-resistant up to 50 meters (5 ATM)
- Sleep quality analysis with REM cycle detection
- 100+ workout modes including running, cycling, swimming, and yoga
- Stress monitoring with guided breathing exercises
- Smartphone notifications and music control
- AMOLED touchscreen display with customizable watch faces

Technical Specifications:
- Display: 1.4" AMOLED, 454x454 resolution
- Battery: 450mAh lithium-ion
- Connectivity: Bluetooth 5.0, Wi-Fi
- Sensors: Optical heart rate, accelerometer, gyroscope, barometer, compass
- Compatibility: iOS 12+ and Android 8+
- Weight: 38 grams
- Materials: Aluminum case with silicone band

Target Audience:
Fitness enthusiasts, athletes, health-conscious professionals aged 25-45 who want comprehensive health tracking and smart notifications without compromising on battery life.

Value Proposition:
Get professional-grade health insights and week-long battery life in a sleek, affordable smartwatch - no daily charging required.`;

// Event Listeners
sourceTypeInputs.forEach(input => {
    input.addEventListener('change', handleSourceTypeChange);
});

contentForm.addEventListener('submit', handleFormSubmit);
loadExampleBtn.addEventListener('click', loadExample);

// Handle source type switching
function handleSourceTypeChange(e) {
    const sourceType = e.target.value;
    
    textInputSection.style.display = 'none';
    urlInputSection.style.display = 'none';
    fileInputSection.style.display = 'none';
    
    if (sourceType === 'text') {
        textInputSection.style.display = 'block';
    } else if (sourceType === 'url') {
        urlInputSection.style.display = 'block';
    } else if (sourceType === 'file') {
        fileInputSection.style.display = 'block';
    }
}

// Load example content
function loadExample() {
    document.getElementById('typeText').checked = true;
    handleSourceTypeChange({ target: { value: 'text' } });
    document.getElementById('contentText').value = exampleContent;
    
    // Show toast notification
    showToast('Example loaded! Click "Generate Content" to start.', 'success');
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Clear previous results
    agentLogsContainer.innerHTML = '';
    outputContentContainer.innerHTML = '';
    statsCard.style.display = 'none';
    
    // Get source type
    const sourceType = document.querySelector('input[name="sourceType"]:checked').value;
    
    // Prepare form data
    const formData = new FormData();
    formData.append('source_type', sourceType);
    
    // Get content based on source type
    if (sourceType === 'text') {
        const content = document.getElementById('contentText').value.trim();
        if (!content) {
            showToast('Please enter some content', 'error');
            return;
        }
        formData.append('content', content);
    } else if (sourceType === 'url') {
        const url = document.getElementById('contentUrl').value.trim();
        if (!url) {
            showToast('Please enter a URL', 'error');
            return;
        }
        formData.append('content', url);
    } else if (sourceType === 'file') {
        const file = document.getElementById('contentFile').files[0];
        if (!file) {
            showToast('Please select a file', 'error');
            return;
        }
        formData.append('file', file);
    }
    
    // Show loading modal
    loadingModal.show();
    
    try {
        // Send request to backend
        const response = await fetch(`${API_BASE_URL}/api/process`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to process content');
        }
        
        const result = await response.json();
        
        // Hide loading modal
        loadingModal.hide();
        
        // Display results
        displayResults(result);
        
        showToast('Content generated successfully!', 'success');
        
    } catch (error) {
        loadingModal.hide();
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Display results
function displayResults(result) {
    if (!result.success) {
        showToast(`Pipeline failed: ${result.error}`, 'error');
        return;
    }
    
    // Display logs
    displayLogs(result.logs);
    
    // Display output content
    displayOutput(result);
    
    // Update stats
    updateStats(result);
}

// Display agent logs
function displayLogs(logs) {
    agentLogsContainer.innerHTML = '';
    
    logs.forEach(log => {
        const logEntry = createLogEntry(log);
        agentLogsContainer.appendChild(logEntry);
    });
    
    // Scroll to bottom
    agentLogsContainer.scrollTop = agentLogsContainer.scrollHeight;
}

// Create log entry element
function createLogEntry(log) {
    const div = document.createElement('div');
    div.className = `log-entry ${log.status}`;
    
    const icon = getStatusIcon(log.status);
    
    let html = `
        <div class="log-agent">
            <i class="bi ${icon} status-icon"></i>
            <span>${log.agent_name}</span>
        </div>
        <div class="log-message">${log.message}</div>
        <div class="log-timestamp">${formatTimestamp(log.timestamp)}</div>
    `;
    
    // Add data if present
    if (log.data && Object.keys(log.data).length > 0) {
        html += `<div class="log-data">${formatLogData(log.data)}</div>`;
    }
    
    div.innerHTML = html;
    return div;
}

// Get status icon
function getStatusIcon(status) {
    const icons = {
        'started': 'bi-play-circle',
        'processing': 'bi-hourglass-split',
        'completed': 'bi-check-circle',
        'error': 'bi-x-circle',
        'revision_needed': 'bi-arrow-clockwise'
    };
    return icons[status] || 'bi-info-circle';
}

// Format timestamp
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

// Format log data
function formatLogData(data) {
    let html = '<ul class="mb-0" style="padding-left: 20px;">';
    for (const [key, value] of Object.entries(data)) {
        if (Array.isArray(value)) {
            html += `<li><strong>${key}:</strong> ${value.length} items</li>`;
            if (value.length > 0 && value.length <= 3) {
                value.forEach(item => {
                    html += `<li class="text-muted" style="list-style: none;">• ${item}</li>`;
                });
            }
        } else {
            html += `<li><strong>${key}:</strong> ${value}</li>`;
        }
    }
    html += '</ul>';
    return html;
}

// Display output content
function displayOutput(result) {
    if (!result.fact_sheet || !result.copywriter_output) {
        outputContentContainer.innerHTML = '<p class="text-muted">No output generated</p>';
        return;
    }
    
    const factSheet = result.fact_sheet;
    const content = result.copywriter_output;
    const feedback = result.editor_feedback;
    
    let html = '';
    
    // Fact Sheet Summary
    html += `
        <div class="output-section">
            <h5><i class="bi bi-clipboard-data"></i> Fact Sheet Summary</h5>
            <div class="fact-sheet-item">
                <strong>Product:</strong> ${factSheet.product_name}
            </div>
            <div class="fact-sheet-item">
                <strong>Features:</strong> ${factSheet.features.length} identified
            </div>
            <div class="fact-sheet-item">
                <strong>Target Audience:</strong> ${factSheet.target_audience}
            </div>
            <div class="fact-sheet-item">
                <strong>Value Proposition:</strong> ${factSheet.value_proposition}
            </div>
        </div>
    `;
    
    // Blog Post
    html += `
        <div class="output-section">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h5><i class="bi bi-file-text"></i> Blog Post</h5>
                <button class="btn btn-sm btn-outline-primary copy-btn" onclick="copyToClipboard('blog')">
                    <i class="bi bi-clipboard"></i> Copy
                </button>
            </div>
            <div class="content" id="blog-content">${formatText(content.blog_post)}</div>
        </div>
    `;
    
    // Social Media Thread
    html += `
        <div class="output-section">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h5><i class="bi bi-share"></i> Social Media Thread</h5>
                <button class="btn btn-sm btn-outline-primary copy-btn" onclick="copyToClipboard('social')">
                    <i class="bi bi-clipboard"></i> Copy
                </button>
            </div>
            <div id="social-content">
    `;
    
    content.social_media_thread.forEach((post, index) => {
        html += `
            <div class="social-post">
                <small class="text-muted">Post ${index + 1}/5</small>
                <div>${post}</div>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    // Email Teaser
    html += `
        <div class="output-section">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h5><i class="bi bi-envelope"></i> Email Teaser</h5>
                <button class="btn btn-sm btn-outline-primary copy-btn" onclick="copyToClipboard('email')">
                    <i class="bi bi-clipboard"></i> Copy
                </button>
            </div>
            <div class="content" id="email-content">${content.email_teaser}</div>
        </div>
    `;
    
    // Editor Feedback
    if (feedback) {
        const statusClass = feedback.approved ? 'success' : 'warning';
        const statusIcon = feedback.approved ? 'check-circle' : 'exclamation-triangle';
        
        html += `
            <div class="output-section">
                <h5><i class="bi bi-shield-check"></i> Quality Review</h5>
                <div class="alert alert-${statusClass} alert-custom">
                    <i class="bi bi-${statusIcon}"></i>
                    <strong>${feedback.approved ? 'Approved' : 'Approved with notes'}</strong>
                </div>
        `;
        
        if (feedback.hallucinations && feedback.hallucinations.length > 0) {
            html += `<div class="mb-2"><strong>Hallucinations detected:</strong> ${feedback.hallucinations.length}</div>`;
        }
        if (feedback.tone_issues && feedback.tone_issues.length > 0) {
            html += `<div class="mb-2"><strong>Tone issues:</strong> ${feedback.tone_issues.length}</div>`;
        }
        
        html += `</div>`;
    }
    
    outputContentContainer.innerHTML = html;
}

// Update stats
function updateStats(result) {
    document.getElementById('iterationCount').textContent = result.iterations;
    document.getElementById('approvalStatus').textContent = result.final_approved ? '✓ Approved' : '⚠ Completed';
    document.getElementById('featuresCount').textContent = result.fact_sheet ? result.fact_sheet.features.length : 0;
    
    statsCard.style.display = 'block';
}

// Format text with paragraphs
function formatText(text) {
    return text.split('\n').map(p => p.trim()).filter(p => p).map(p => `<p>${p}</p>`).join('');
}

// Copy to clipboard
function copyToClipboard(type) {
    let text = '';
    
    if (type === 'blog') {
        text = document.getElementById('blog-content').innerText;
    } else if (type === 'social') {
        text = document.getElementById('social-content').innerText;
    } else if (type === 'email') {
        text = document.getElementById('email-content').innerText;
    }
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        showToast('Failed to copy', 'error');
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const colors = {
        success: 'bg-success',
        error: 'bg-danger',
        info: 'bg-info',
        warning: 'bg-warning'
    };
    
    const toast = document.createElement('div');
    toast.className = `position-fixed bottom-0 end-0 p-3`;
    toast.style.zIndex = '11';
    
    toast.innerHTML = `
        <div class="toast show" role="alert">
            <div class="toast-header ${colors[type]} text-white">
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Autonomous Content Factory initialized');
});