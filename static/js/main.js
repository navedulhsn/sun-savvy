// SunSavvy Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Initialize chatbot
    initChatbot();

    // Auto-dismiss alerts after 5 seconds
    autoDismissAlerts();

    // Clean any stuck Bootstrap modal backdrops (prevents dim screen)
    cleanupModalBackdrops();

    // Ensure future modals also clean up properly
    document.querySelectorAll('.modal').forEach(function (modalEl) {
        modalEl.addEventListener('hidden.bs.modal', function () {
            cleanupModalBackdrops();
        });
    });
});

// Chatbot functionality
function initChatbot() {
    const toggle = document.getElementById('chatbot-toggle');
    const panel = document.getElementById('chatbot-panel');
    const closeBtn = document.getElementById('chatbot-close');
    const sendBtn = document.getElementById('chatbot-send');
    const input = document.getElementById('chatbot-input');
    const messages = document.getElementById('chatbot-messages');

    if (!toggle || !panel) return;

    // Toggle chatbot panel
    toggle.addEventListener('click', function () {
        panel.classList.toggle('d-none');
        if (!panel.classList.contains('d-none')) {
            input.focus();
        }
    });

    // Close chatbot
    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            panel.classList.add('d-none');
        });
    }

    // Send message
    function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, 'user');
        input.value = '';

        // Send to backend
        fetch('/api/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: message })
        })
            .then(response => response.json())
            .then(data => {
                if (data.response) {
                    addMessage(data.response, 'bot');
                } else if (data.error) {
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('Sorry, I\'m having trouble connecting. Please try again later.', 'bot');
            });
    }

    // Send button click
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    // Enter key press
    if (input) {
        input.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // Add welcome message
    setTimeout(() => {
        if (messages && messages.children.length === 0) {
            addMessage('Hello! I\'m SunSavvy Assistant. How can I help you with solar energy today?', 'bot');
        }
    }, 500);
}

// Add message to chatbot
function addMessage(text, type) {
    const messages = document.getElementById('chatbot-messages');
    if (!messages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message ${type}`;
    messageDiv.textContent = text;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Auto-dismiss alerts
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Form validation enhancement
document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(function (field) {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        if (!isValid) {
            e.preventDefault();
        }
    });
});

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Clean up any stray Bootstrap modal backdrops that might block the UI
function cleanupModalBackdrops() {
    // Remove leftover backdrop overlays
    document.querySelectorAll('.modal-backdrop').forEach(function (el) {
        if (el && el.parentNode) {
            el.parentNode.removeChild(el);
        }
    });
    // Reset body state if a backdrop got stuck
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
}

