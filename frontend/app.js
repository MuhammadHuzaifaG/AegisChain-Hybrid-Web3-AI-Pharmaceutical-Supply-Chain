// ==========================================
// App Configuration & State
// ==========================================
const API_BASE_URL = 'http://localhost:8000/api/v1'; // Update to cloud URL for live deployment

// ==========================================
// DOM Elements
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initForms();
    initAuditEngine();
});

// ==========================================
// Tab Navigation Logic
// ==========================================
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    navButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Remove active state from all buttons
            navButtons.forEach(b => b.classList.remove('active'));
            // Hide all tabs
            tabContents.forEach(tab => {
                tab.classList.add('hidden');
                tab.classList.remove('animate-fade');
            });

            // Activate clicked button
            const targetBtn = e.currentTarget;
            targetBtn.classList.add('active');

            // Show target tab with animation
            const targetTabId = targetBtn.getAttribute('data-tab');
            const targetTab = document.getElementById(targetTabId);
            
            if (targetTab) {
                targetTab.classList.remove('hidden');
                // Trigger reflow to restart CSS animation
                void targetTab.offsetWidth; 
                targetTab.classList.add('animate-fade');
            }
        });
    });
}

// ==========================================
// Form Handling & API Integration
// ==========================================
function initForms() {
    const registerForm = document.getElementById('form-register');
    const transitForm = document.getElementById('form-transit');

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            try {
                setLoadingState(submitBtn, true);
                
                const payload = {
                    batch_id: document.getElementById('reg-batch-id').value,
                    medicine_name: document.getElementById('reg-med-name').value,
                    data_hash: document.getElementById('reg-data-hash').value
                };

                const response = await fetch(`${API_BASE_URL}/batches`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) throw new Error('Failed to register batch on ledger.');
                
                const data = await response.json();
                showFeedback('reg-feedback', `Success! Tx Hash: ${data.transaction_hash.substring(0, 15)}...`, 'success');
                registerForm.reset();
            } catch (error) {
                showFeedback('reg-feedback', error.message, 'error');
            } finally {
                setLoadingState(submitBtn, false, originalText);
            }
        });
    }

    if (transitForm) {
        transitForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = transitForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            try {
                setLoadingState(submitBtn, true);

                const payload = {
                    batch_id: document.getElementById('trans-batch-id').value,
                    location: document.getElementById('trans-location').value,
                    temperature_celsius: parseFloat(document.getElementById('trans-temp').value),
                    humidity_percent: parseFloat(document.getElementById('trans-hum').value) || null
                };

                const response = await fetch(`${API_BASE_URL}/transit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) throw new Error('Failed to record transit telemetry.');

                const data = await response.json();
                showFeedback('trans-feedback', `Success! Telemetry logged. Tx Hash: ${data.transaction_hash.substring(0, 15)}...`, 'success');
                transitForm.reset();
            } catch (error) {
                showFeedback('trans-feedback', error.message, 'error');
            } finally {
                setLoadingState(submitBtn, false, originalText);
            }
        });
    }
}

// ==========================================
// AI Audit & Verification Engine
// ==========================================
function initAuditEngine() {
    const auditBtn = document.getElementById('btn-audit');
    const auditInput = document.getElementById('audit-batch-id');

    if (auditBtn && auditInput) {
        auditBtn.addEventListener('click', async () => {
            const batchId = auditInput.value.trim();
            if (!batchId) return alert('Please enter a Batch ID.');

            const originalText = auditBtn.innerHTML;
            const resultsContainer = document.getElementById('audit-results');
            
            try {
                setLoadingState(auditBtn, true);
                
                // Fetch history and trigger AI analysis
                const response = await fetch(`${API_BASE_URL}/batches/${batchId}/history?analyze=true`);
                if (!response.ok) throw new Error('Batch not found or API error.');

                const data = await response.json();
                
                // Render UI
                resultsContainer.classList.remove('hidden');
                renderAIAssessment(data.ai_analysis);
                renderTimeline(data.transit_history);

            } catch (error) {
                alert(`Audit Failed: ${error.message}`);
                resultsContainer.classList.add('hidden');
            } finally {
                setLoadingState(auditBtn, false, originalText);
            }
        });
    }
}

function renderAIAssessment(aiData) {
    if (!aiData) return;

    const box = document.getElementById('ai-assessment-box');
    const badge = document.getElementById('ai-status-badge');
    
    // Update Badge & Styles
    badge.textContent = aiData.status;
    badge.className = `status-badge ${aiData.status.toLowerCase()}`;
    
    if (aiData.status.toLowerCase() === 'compromised') {
        box.classList.add('danger');
    } else {
        box.classList.remove('danger');
    }

    // Update Text Data
    document.getElementById('ai-summary-text').textContent = aiData.summary;
    document.getElementById('ai-confidence').textContent = (aiData.confidence_score * 100).toFixed(0);
    document.getElementById('ai-anomalies').textContent = aiData.anomalies_detected;
}

function renderTimeline(history) {
    const timelineContainer = document.getElementById('transit-timeline');
    timelineContainer.innerHTML = ''; // Clear previous

    if (!history || history.length === 0) {
        timelineContainer.innerHTML = '<p style="color: var(--text-muted)">No transit history recorded yet.</p>';
        return;
    }

    history.forEach((record, index) => {
        // Format timestamp securely
        const dateObj = new Date(record.timestamp);
        const timeString = isNaN(dateObj) ? record.timestamp : dateObj.toLocaleString();

        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.innerHTML = `
            <div class="timeline-content">
                <h4 style="margin-bottom: 0.5rem; color: var(--primary-color);">${record.location}</h4>
                <p style="font-size: 0.9rem; margin-bottom: 0.3rem;"><i class="fa-regular fa-clock"></i> ${timeString}</p>
                <p style="font-size: 0.9rem; margin-bottom: 0.3rem;"><i class="fa-solid fa-temperature-half"></i> ${record.temperature_data}</p>
                <p style="font-size: 0.75rem; color: var(--text-muted);"><i class="fa-solid fa-fingerprint"></i> Handler: ${record.handler_address}</p>
            </div>
        `;
        timelineContainer.appendChild(item);
    });
}

// ==========================================
// UI Utility Functions
// ==========================================
function setLoadingState(button, isLoading, originalText = '') {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';
        button.style.opacity = '0.7';
    } else {
        button.disabled = false;
        button.innerHTML = originalText;
        button.style.opacity = '1';
    }
}

function showFeedback(elementId, message, type) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    el.textContent = message;
    el.style.marginTop = '1rem';
    el.style.padding = '1rem';
    el.style.borderRadius = '8px';
    el.style.fontSize = '0.9rem';
    el.style.fontWeight = '600';
    
    if (type === 'success') {
        el.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
        el.style.color = 'var(--accent-color)';
        el.style.border = '1px solid var(--accent-color)';
    } else {
        el.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
        el.style.color = 'var(--danger-color)';
        el.style.border = '1px solid var(--danger-color)';
    }

    // Auto-hide after 5 seconds
    setTimeout(() => {
        el.textContent = '';
        el.style.padding = '0';
        el.style.border = 'none';
    }, 5000);
}