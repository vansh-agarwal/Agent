/**
 * ARIA - AI Personal Task Automation Agent
 * Premium Frontend Application
 * Award-Winning Hackathon Quality
 */

// ==================== CONFIGURATION ====================
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5000/api'
    : 'https://disciplined-embrace-production-9079.up.railway.app/api';

// ==================== STATE ====================
const state = {
    tasks: [],
    events: [],
    systemStatus: { integrations: {} },
    chatHistory: [],
    isTyping: false
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initializeUser();
    initializeApp();
    setupEventListeners();
    startAutoRefresh();
    animateOnScroll();
});

// Initialize user greeting
function initializeUser() {
    const userData = localStorage.getItem('aria_user');
    if (userData) {
        const user = JSON.parse(userData);
        const greeting = document.getElementById('userGreeting');
        if (greeting && user.name) {
            greeting.textContent = `Welcome, ${user.name.split(' ')[0]}!`;
        }
        // Load user-specific data
        loadUserData(user.email);
    }
}

// Load user-specific data from backend
async function loadUserData(userEmail) {
    // This ensures each user sees only their own data
    // In a real app, the backend would filter by authenticated user
    console.log(`Loading data for user: ${userEmail}`);
}

// Logout handler - properly clear all session data
function handleLogout() {
    // Clear all localStorage data to prevent contamination
    localStorage.removeItem('aria_user');

    // Clear any cached state
    state.tasks = [];
    state.events = [];
    state.chatHistory = [];

    // Clear the chat UI
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.innerHTML = '';
    }

    // Redirect to homepage
    window.location.href = 'index.html';
}

async function initializeApp() {
    updateStatus('Connecting...');

    // Clear existing state to prevent duplicates on reload
    state.tasks = [];
    state.events = [];

    try {
        await Promise.all([
            fetchSystemStatus(),
            fetchTasks(),
            fetchEvents()
        ]);

        // Show connected status
        console.log('✅ ARIA connected successfully');

    } catch (error) {
        console.error('Initialization error:', error);
        showConnectionError();
    }
}

function showConnectionError() {
    updateStatus('Offline Mode', '#ef4444');

    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="chat-message assistant">
            <div class="chat-bubble" style="border-color: rgba(239, 68, 68, 0.3);">
                <strong>⚠️ Backend Server Not Detected</strong><br><br>
                To start the full experience:<br>
                <code style="display: block; margin: 12px 0; padding: 12px; background: rgba(0,0,0,0.4); border-radius: 8px; font-family: monospace;">
                cd c:\\Users\\vansh\\Desktop\\Hackathon<br>
                python backend/app.py
                </code>
                <br>
                Then refresh this page. Or continue in offline demo mode!
            </div>
        </div>
    `;
}

function updateStatus(text, color = null) {
    const statusText = document.getElementById('statusText');
    statusText.textContent = text;
    if (color) {
        statusText.style.color = color;
    }
}

function setupEventListeners() {
    // Chat
    document.getElementById('sendChatBtn').addEventListener('click', sendChatMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });

    // Chat input animation
    const chatInput = document.getElementById('chatInput');
    chatInput.addEventListener('focus', () => {
        chatInput.parentElement.style.transform = 'scale(1.01)';
    });
    chatInput.addEventListener('blur', () => {
        chatInput.parentElement.style.transform = 'scale(1)';
    });

    // Tasks
    document.getElementById('addTaskBtn').addEventListener('click', showTaskForm);
    document.getElementById('saveTaskBtn').addEventListener('click', createTask);
    document.getElementById('cancelTaskBtn').addEventListener('click', hideTaskForm);

    // Events
    document.getElementById('addEventBtn').addEventListener('click', showEventForm);
    document.getElementById('saveEventBtn').addEventListener('click', createEvent);
    document.getElementById('cancelEventBtn').addEventListener('click', hideEventForm);

    // Email
    document.getElementById('sendEmailBtn').addEventListener('click', sendEmail);

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus chat
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('chatInput').focus();
        }
    });
}

function startAutoRefresh() {
    setInterval(async () => {
        await fetchTasks();
        await fetchEvents();
    }, 30000);
}

function animateOnScroll() {
    // Simplified animation - cards are visible by default
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '1';
        card.style.transition = 'all 0.3s ease';
    });
}

// ==================== API CALLS ====================
async function apiCall(endpoint, options = {}) {
    try {
        // Get user email for data isolation
        const userData = localStorage.getItem('aria_user');
        let userEmail = 'anonymous@demo.com';
        if (userData) {
            try {
                const user = JSON.parse(userData);
                userEmail = user.email || 'anonymous@demo.com';
            } catch (e) {
                console.error('Error parsing user data:', e);
            }
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                'X-User-Email': userEmail,  // Add user email for backend filtering
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        return null;
    }
}

async function fetchSystemStatus() {
    const data = await apiCall('/status');
    if (data) {
        state.systemStatus = data;
        updateStatusBadge(data);
    }
}

async function fetchTasks() {
    const data = await apiCall('/tasks?prioritize=true');
    if (data && data.tasks) {
        state.tasks = data.tasks;
        renderTasks();
        updateStats();
    }
}

async function fetchEvents() {
    const data = await apiCall('/events');
    if (data && data.events) {
        state.events = data.events;
        renderEvents();
        updateStats();
    }
}

// ==================== CHAT ====================
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message || state.isTyping) return;

    // Add user message with animation
    addChatMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    state.isTyping = true;
    const typingId = showTypingIndicator();

    // Disable input while processing
    input.disabled = true;

    // Send to API
    const data = await apiCall('/chat', {
        method: 'POST',
        body: JSON.stringify({ message })
    });

    // Remove typing indicator
    removeTypingIndicator(typingId);
    state.isTyping = false;
    input.disabled = false;
    input.focus();

    if (data) {
        // Add AI response with typewriter effect
        addChatMessage(data.response || 'I processed your request!', 'assistant');

        // Refresh data if action was performed
        if (data.action_result && data.action_result.success) {
            await fetchTasks();
            await fetchEvents();

            // Show success notification with appropriate message
            const messages = {
                'task_created': '✅ Task created successfully!',
                'event_created': '📅 Event scheduled!',
                'email_sent': '📧 Email sent!'
            };
            showNotification(messages[data.action_result.type] || 'Action completed!', 'success');
        }
    } else {
        addChatMessage('Sorry, I couldn\'t process that request. Please check if the server is running.', 'assistant');
    }

    scrollChatToBottom();
}

function addChatMessage(text, role) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    const messageId = Date.now();

    messageDiv.className = `chat-message ${role}`;
    messageDiv.id = `msg-${messageId}`;
    messageDiv.innerHTML = `
        <div class="chat-bubble">${formatMessage(text)}</div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollChatToBottom();

    return messageId;
}

function formatMessage(text) {
    // Escape HTML but allow our formatting
    return text
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>')
        .replace(/`([^`]+)`/g, '<code style="background: rgba(124,58,237,0.2); padding: 2px 6px; border-radius: 4px;">$1</code>');
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    const typingId = `typing-${Date.now()}`;

    typingDiv.className = 'chat-message assistant';
    typingDiv.id = typingId;
    typingDiv.innerHTML = `
        <div class="chat-bubble">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    messagesContainer.appendChild(typingDiv);
    scrollChatToBottom();

    return typingId;
}

function removeTypingIndicator(typingId) {
    const typingElement = document.getElementById(typingId);
    if (typingElement) {
        typingElement.style.opacity = '0';
        typingElement.style.transform = 'translateY(-10px)';
        setTimeout(() => typingElement.remove(), 300);
    }
}

function scrollChatToBottom() {
    const container = document.getElementById('chatMessages');
    container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth'
    });
}

// ==================== TASK MANAGEMENT ====================
function showTaskForm() {
    const form = document.getElementById('taskForm');
    form.classList.add('show');
    document.getElementById('taskTitle').focus();
    document.getElementById('addTaskBtn').style.display = 'none';
}

function hideTaskForm() {
    const form = document.getElementById('taskForm');
    form.classList.remove('show');
    clearTaskForm();
    document.getElementById('addTaskBtn').style.display = '';
}

function clearTaskForm() {
    document.getElementById('taskTitle').value = '';
    document.getElementById('taskDescription').value = '';
    document.getElementById('taskPriority').value = 'MEDIUM';
    document.getElementById('taskDeadline').value = '';
}

async function createTask() {
    const title = document.getElementById('taskTitle').value.trim();
    const description = document.getElementById('taskDescription').value.trim();
    const priority = document.getElementById('taskPriority').value;
    const deadline = document.getElementById('taskDeadline').value;

    if (!title) {
        showNotification('Please enter a task title', 'error');
        document.getElementById('taskTitle').focus();
        return;
    }

    const btn = document.getElementById('saveTaskBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span>';

    const taskData = {
        title,
        description,
        priority,
        status: 'todo',
        deadline: deadline || null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        tags: []
    };

    const data = await apiCall('/tasks', {
        method: 'POST',
        body: JSON.stringify(taskData)
    });

    btn.disabled = false;
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg> Save';

    if (data && data.success) {
        showNotification('✅ Task created!', 'success');
        hideTaskForm();
        await fetchTasks();
    }
}

async function toggleTaskComplete(taskId) {
    const task = state.tasks.find(t => t.id === taskId);
    if (!task) return;

    const newStatus = task.status === 'completed' ? 'todo' : 'completed';

    // Optimistic update
    const taskElement = document.querySelector(`.task-item[data-id="${taskId}"]`);
    if (taskElement) {
        taskElement.style.transform = 'scale(0.98)';
        setTimeout(() => taskElement.style.transform = '', 200);
    }

    const data = await apiCall(`/tasks/${taskId}`, {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus })
    });

    if (data && data.success) {
        await fetchTasks();
        if (newStatus === 'completed') {
            showNotification('🎉 Task completed!', 'success');
        }
    }
}

async function deleteTask(taskId) {
    if (!taskId) {
        showNotification('Error: No task ID', 'error');
        return;
    }

    // Visual feedback
    const taskElement = document.querySelector(`.item[data-id="${taskId}"]`);
    if (taskElement) {
        taskElement.style.opacity = '0.5';
    }

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Email': getUserEmail()
            }
        });

        if (response.ok) {
            // Remove from local state immediately
            state.tasks = state.tasks.filter(t => t.id !== taskId);
            renderTasks();
            updateStats();
            showNotification('✓ Task deleted', 'success');
        } else {
            if (taskElement) taskElement.style.opacity = '';
            showNotification('Failed to delete task', 'error');
        }
    } catch (error) {
        console.error('Delete task error:', error);
        if (taskElement) taskElement.style.opacity = '';
        showNotification('Error deleting task', 'error');
    }
}

function renderTasks() {
    const container = document.getElementById('taskList');

    if (!state.tasks || state.tasks.length === 0) {
        container.innerHTML = `
            <div class="empty">
                <div class="empty-icon">📋</div>
                No tasks yet
            </div>
        `;
        return;
    }

    container.innerHTML = state.tasks.map(task => `
        <div class="item ${task.status === 'completed' ? 'completed' : ''}" data-id="${task.id}">
            <div class="item-header">
                <div class="item-title">${escapeHtml(task.title || 'Untitled')}</div>
                <div style="display: flex; gap: 6px;">
                    <button type="button" class="btn-secondary btn-icon btn-small" 
                            onclick="window.toggleTaskComplete(${task.id})" 
                            title="${task.status === 'completed' ? 'Mark incomplete' : 'Complete'}"
                            style="cursor: pointer;">
                        ${task.status === 'completed' ? '↩️' : '✓'}
                    </button>
                    <button type="button" class="btn-secondary btn-icon btn-small" 
                            onclick="window.deleteTask(${task.id})" 
                            title="Delete"
                            style="cursor: pointer;">
                        ✕
                    </button>
                </div>
            </div>
            ${task.description ? `<div class="item-desc">${escapeHtml(task.description)}</div>` : ''}
            <div class="item-meta">
                <span class="priority priority-${task.priority || 'MEDIUM'}">${task.priority || 'MEDIUM'}</span>
                ${task.deadline ? `<span>📅 ${formatDate(task.deadline)}</span>` : ''}
            </div>
        </div>
    `).join('');
}

// ==================== CALENDAR MANAGEMENT ====================
function showEventForm() {
    const form = document.getElementById('eventForm');
    form.classList.add('show');

    // Set default start time to next hour
    const nextHour = new Date();
    nextHour.setHours(nextHour.getHours() + 1, 0, 0, 0);
    document.getElementById('eventStart').value = formatDateTimeLocal(nextHour);

    document.getElementById('eventTitle').focus();
    document.getElementById('addEventBtn').style.display = 'none';
}

function hideEventForm() {
    document.getElementById('eventForm').classList.remove('show');
    clearEventForm();
    document.getElementById('addEventBtn').style.display = '';
}

function clearEventForm() {
    document.getElementById('eventTitle').value = '';
    document.getElementById('eventStart').value = '';
    document.getElementById('eventDuration').value = '60';
    document.getElementById('eventLocation').value = '';
}

async function createEvent() {
    const title = document.getElementById('eventTitle').value.trim();
    const startTime = document.getElementById('eventStart').value;
    const duration = parseInt(document.getElementById('eventDuration').value) || 60;
    const location = document.getElementById('eventLocation').value.trim();

    if (!title || !startTime) {
        showNotification('Please fill in event details', 'error');
        return;
    }

    const btn = document.getElementById('saveEventBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span>';

    const start = new Date(startTime);
    const end = new Date(start.getTime() + duration * 60000);

    const eventData = {
        title,
        description: '',
        start_time: start.toISOString(),
        end_time: end.toISOString(),
        location,
        attendees: []
    };

    const data = await apiCall('/events', {
        method: 'POST',
        body: JSON.stringify(eventData)
    });

    btn.disabled = false;
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg> Create';

    if (data && data.success) {
        showNotification('📅 Event created!', 'success');
        hideEventForm();
        await fetchEvents();
    }
}

async function deleteEvent(eventId) {
    if (!eventId) {
        showNotification('Error: No event ID', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/events/${eventId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Email': getUserEmail()
            }
        });

        if (response.ok) {
            // Remove from local state immediately
            state.events = state.events.filter(e => String(e.id) !== String(eventId));
            renderEvents();
            updateStats();
            showNotification('✓ Event deleted', 'success');
        } else {
            showNotification('Failed to delete event', 'error');
        }
    } catch (error) {
        console.error('Delete event error:', error);
        showNotification('Error deleting event', 'error');
    }
}

function getUserEmail() {
    try {
        const user = JSON.parse(localStorage.getItem('aria_user') || '{}');
        return user.email || 'demo@aria.app';
    } catch {
        return 'demo@aria.app';
    }
}

function renderEvents() {
    const container = document.getElementById('calendarView');

    // Filter events: only today and future, remove duplicates
    const now = new Date();
    now.setHours(0, 0, 0, 0);

    const seen = new Set();
    const filteredEvents = (state.events || [])
        .filter(event => {
            // Filter by date - only today and future
            const eventDate = new Date(event.start_time);
            if (eventDate < now) return false;

            // Remove duplicates by title + start_time
            const key = `${event.title}-${event.start_time}`;
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
        })
        .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
        .slice(0, 10); // Limit to 10 events

    if (filteredEvents.length === 0) {
        container.innerHTML = `
            <div class="empty">
                <div class="empty-icon">📆</div>
                No upcoming events
            </div>
        `;
        return;
    }

    container.innerHTML = filteredEvents.map(event => `
        <div class="item" style="position: relative;" data-event-id="${event.id}">
            <div class="item-header">
                <div>
                    <div style="font-size: 12px; color: var(--primary); font-weight: 600; margin-bottom: 4px;">
                        ${formatEventTime(event.start_time)}
                    </div>
                    <div class="item-title">${escapeHtml(event.title || 'Untitled')}</div>
                </div>
                <button type="button" class="btn-secondary btn-icon btn-small" 
                        onclick="window.deleteEvent('${event.id}')" 
                        title="Delete event"
                        style="cursor: pointer;">
                    ✕
                </button>
            </div>
            ${event.location ? `<div class="item-meta">📍 ${escapeHtml(event.location)}</div>` : ''}
        </div>
    `).join('');
}

// ==================== EMAIL ====================
async function sendEmail() {
    const recipient = document.getElementById('emailRecipient').value.trim();
    const subject = document.getElementById('emailSubject').value.trim();
    const body = document.getElementById('emailBody').value.trim();

    if (!recipient || !subject || !body) {
        showNotification('⚠️ Please fill all email fields', 'error');
        return;
    }

    if (!isValidEmail(recipient)) {
        showNotification('⚠️ Please enter a valid email address', 'error');
        return;
    }

    const btn = document.getElementById('sendEmailBtn');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Sending...';

    try {
        const data = await apiCall('/emails/send', {
            method: 'POST',
            body: JSON.stringify({ recipient, subject, body })
        });

        if (data && data.success) {
            showNotification('✅ Email sent successfully!', 'success');
            // Clear form
            document.getElementById('emailRecipient').value = '';
            document.getElementById('emailSubject').value = '';
            document.getElementById('emailBody').value = '';

            // Add to chat as confirmation
            addChatMessage(
                `📧 Email sent to ${recipient}\n\nSubject: ${subject}`,
                'assistant'
            );
        } else {
            const errorMsg = data?.error || 'Unknown error';
            showNotification(`❌ Failed to send email: ${errorMsg}`, 'error');
        }
    } catch (error) {
        console.error('Email send error:', error);
        showNotification('❌ Error sending email. Check connection.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
}

// ==================== UI UPDATES ====================
function updateStatusBadge(status) {
    const statusText = document.getElementById('statusText');
    const statusDot = document.querySelector('.status-dot');

    // If we got a response from the backend, we're connected
    if (status && status.status === 'running') {
        statusText.textContent = 'Connected';
        statusText.style.color = '#10b981';
        if (statusDot) statusDot.style.background = '#10b981';
    } else {
        statusText.textContent = 'Demo Mode';
        statusText.style.color = '#a855f7';
        if (statusDot) statusDot.style.background = '#a855f7';
    }
}

function updateStats() {
    const activeTasks = state.tasks.filter(t => t.status !== 'completed').length;
    const completedToday = state.tasks.filter(t => {
        if (t.status !== 'completed') return false;
        const updated = new Date(t.updated_at);
        const today = new Date();
        return updated.toDateString() === today.toDateString();
    }).length;

    // Animate numbers
    animateNumber('statTasks', activeTasks);
    animateNumber('statEvents', state.events.length);
    animateNumber('statCompleted', completedToday);
}

function animateNumber(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return; // Element might not exist in simplified UI

    const currentValue = parseInt(element.textContent) || 0;

    if (currentValue === targetValue) return;

    const duration = 500;
    const steps = 20;
    const increment = (targetValue - currentValue) / steps;
    let current = currentValue;
    let step = 0;

    const timer = setInterval(() => {
        step++;
        current += increment;
        element.textContent = Math.round(current);

        if (step >= steps) {
            element.textContent = targetValue;
            clearInterval(timer);
        }
    }, duration / steps);
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    document.querySelectorAll('.notification').forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'notification-slide 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ==================== UTILITIES ====================
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((date - now) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays === -1) return 'Yesterday';
    if (diffDays < 7 && diffDays > 0) return `In ${diffDays} days`;
    if (diffDays < 0) return 'Overdue';

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatEventTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

function formatDateTimeLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ==================== GLOBAL FUNCTIONS ====================
window.toggleTaskComplete = toggleTaskComplete;
window.deleteTask = deleteTask;
window.deleteEvent = deleteEvent;
window.handleLogout = handleLogout;

// ==================== EASTER EGGS ====================
console.log('%c🚀 ARIA - AI Personal Task Automation', 'font-size: 20px; font-weight: bold; color: #7c3aed;');
console.log('%cBuilt for DSARG_2 Hackathon', 'font-size: 12px; color: #a855f7;');
console.log('%cPress Ctrl+K to quickly access ARIA!', 'font-size: 11px; color: #64748b;');
