// Theme Toggle
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const icon = themeToggle.querySelector('i');

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        body.className = savedTheme;
        icon.className = savedTheme === 'dark-mode' ? 'fas fa-sun' : 'fas fa-moon';
    }

    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        body.classList.toggle('light-mode');
        
        // Update icon
        if (body.classList.contains('dark-mode')) {
            icon.className = 'fas fa-sun';
            localStorage.setItem('theme', 'dark-mode');
        } else {
            icon.className = 'fas fa-moon';
            localStorage.setItem('theme', 'light-mode');
        }
    });
});

// Chatbot functionality
function initializeChatbot() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const downloadButton = document.getElementById('download-chat');

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;

            // Add user message
            appendMessage('user', message);
            chatInput.value = '';

            // Show loading spinner
            const loadingSpinner = document.createElement('div');
            loadingSpinner.className = 'spinner mx-auto my-3';
            chatMessages.appendChild(loadingSpinner);

            try {
                const response = await fetch('/get-ai-response', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message }),
                });

                const data = await response.json();
                
                // Remove loading spinner
                loadingSpinner.remove();
                
                // Add bot response
                appendMessage('bot', data.response);
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } catch (error) {
                console.error('Error:', error);
                loadingSpinner.remove();
                appendMessage('bot', 'Sorry, I encountered an error. Please try again.');
            }
        });
    }

    if (downloadButton) {
        downloadButton.addEventListener('click', () => {
            const messages = Array.from(chatMessages.children)
                .map(msg => {
                    const type = msg.classList.contains('user-message') ? 'User' : 'Bot';
                    const content = msg.textContent;
                    return `${type}: ${content}`;
                })
                .join('\n\n');

            const blob = new Blob([messages], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'chat-history.txt';
            a.click();
            window.URL.revokeObjectURL(url);
        });
    }
}

function appendMessage(type, content) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}-message fade-in`;
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
}

// BMI Calculator
function initializeBMICalculator() {
    const bmiForm = document.getElementById('bmi-form');
    if (bmiForm) {
        bmiForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const weight = document.getElementById('weight').value;
            const height = document.getElementById('height').value;

            try {
                const response = await fetch('/calculate-bmi', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ weight, height }),
                });

                const data = await response.json();
                document.getElementById('bmi-result').textContent = `Your BMI: ${data.bmi.toFixed(2)}`;
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }
}

// Diet Plan Generator
function initializeDietPlanGenerator() {
    const dietForm = document.getElementById('diet-form');
    if (dietForm) {
        dietForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = {
                category: document.getElementById('category').value,
                foodType: document.getElementById('food-type').value,
                dietType: document.getElementById('diet-type').value,
                bmi: document.getElementById('bmi').value
            };

            try {
                const response = await fetch('/generate-diet-plan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData),
                });

                const data = await response.json();
                document.getElementById('diet-plan-result').innerHTML = data.plan.replace(/\n/g, '<br>');
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }
}

// Initialize all features
document.addEventListener('DOMContentLoaded', () => {
    initializeChatbot();
    initializeBMICalculator();
    initializeDietPlanGenerator();
}); 