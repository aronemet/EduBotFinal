/**
 * EduBot Frontend - Chat Interface Logic
 * Handles UI interactions, API communication, and conversation management
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

// Dynamic API endpoint - works locally and when deployed
const API_BASE_URL = (() => {
    // For local development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8001';
    }
    // For deployed version (replace with your actual backend URL after deployment)
    // Example: If backend is deployed to Render.com, it might be 'https://your-backend.onrender.com'
    return 'https://edubot-backend.onrender.com'; // Default deployed URL (update after deployment)
})();

const STORAGE_KEY = 'edubot_conversations';
const THEME_KEY = 'edubot_theme';

// Faster response settings
const FAST_MODE = {
    temperature: 0.5,
    max_tokens: 512
};

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

let currentConversation = {
    id: generateId(),
    title: 'New Chat',
    messages: [],
    createdAt: new Date().toISOString(),
};

let conversations = [];
let isLoading = false;

// ============================================================================
// DOM ELEMENTS
// ============================================================================

const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');
const conversationsList = document.getElementById('conversationsList');
const themeToggle = document.getElementById('themeToggle');
const loadingIndicator = document.getElementById('loadingIndicator');
const toastContainer = document.getElementById('toastContainer');
const statusIndicator = document.getElementById('statusIndicator');

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    loadConversations();
    checkBackendStatus();
    loadTheme();
});

function initializeApp() {
    console.log('🚀 EduBot initialized');
    renderWelcomeMessage();
}

function setupEventListeners() {
    sendBtn.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            handleSendMessage();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
    });
    
    newChatBtn.addEventListener('click', startNewChat);
    themeToggle.addEventListener('click', toggleTheme);
}

// ============================================================================
// BACKEND COMMUNICATION
// ============================================================================

async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            statusIndicator.style.color = '#10a37f';
            console.log('✓ Backend connected');
        }
    } catch (error) {
        statusIndicator.style.color = '#ef4444';
        console.error('✗ Backend connection failed:', error);
        showToast('Backend not available. Make sure the server is running.', 'error');
    }
}

async function sendChatMessage(messages) {
    try {
        setLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messages: messages.slice(-3), // Only send last 3 messages for speed
                ...FAST_MODE
            }),
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Error sending message:', error);
        showToast('Failed to get response. Check backend connection.', 'error');
        throw error;
    } finally {
        setLoading(false);
    }
}

// ============================================================================
// MESSAGE HANDLING
// ============================================================================

async function handleSendMessage() {
    const message = messageInput.value.trim();
    
    if (!message) return;
    if (isLoading) return;
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Remove welcome message if first message
    if (currentConversation.messages.length === 0) {
        messagesContainer.innerHTML = '';
    }
    
    // Add user message to conversation
    currentConversation.messages.push({
        role: 'user',
        content: message,
    });
    
    // Render user message
    renderMessage('user', message);
    
    try {
        // Get AI response
        const response = await sendChatMessage(currentConversation.messages);
        
        // Add assistant message to conversation
        currentConversation.messages.push({
            role: 'assistant',
            content: response,
        });
        
        // Render assistant message
        renderMessage('assistant', response);
        
        // Update conversation title if first message
        if (currentConversation.messages.length === 2) {
            currentConversation.title = message.substring(0, 50) + (message.length > 50 ? '...' : '');
        }
        
        // Save conversation
        saveConversations();
        updateConversationsList();
        
    } catch (error) {
        console.error('Error:', error);
    }
}

function renderMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessageContent(content);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatMessageContent(content) {
    // Simplified formatting for speed
    let formatted = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // Basic markdown
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\*(.*?)\*/g, '<em>$1</em>')
                        .replace(/`(.*?)`/g, '<code>$1</code>')
                        .replace(/\n/g, '<br>');
    
    return formatted;
}

function renderWelcomeMessage() {
    messagesContainer.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">🎓</div>
            <h2>EduBot - Fast Learning Assistant</h2>
            <p>Ask me anything and I'll help you understand concepts through guided learning!</p>
            
            <div class="example-prompts">
                <button class="example-btn" onclick="sendMessage('How does photosynthesis work?')">
                    How does photosynthesis work?
                </button>
                <button class="example-btn" onclick="sendMessage('Explain derivatives in calculus')">
                    Explain derivatives in calculus
                </button>
                <button class="example-btn" onclick="sendMessage('Help me understand the French Revolution')">
                    Help me understand the French Revolution
                </button>
            </div>
        </div>
    `;
}

function sendMessage(text) {
    messageInput.value = text;
    messageInput.focus();
    handleSendMessage();
}

// ============================================================================
// CONVERSATION MANAGEMENT
// ============================================================================

function startNewChat() {
    // Save current conversation if it has messages
    if (currentConversation.messages.length > 0) {
        saveConversations();
    }
    
    // Create new conversation
    currentConversation = {
        id: generateId(),
        title: 'New Chat',
        messages: [],
        createdAt: new Date().toISOString(),
    };
    
    renderWelcomeMessage();
    updateConversationsList();
}

function loadConversation(id) {
    const conversation = conversations.find(c => c.id === id);
    if (conversation) {
        currentConversation = JSON.parse(JSON.stringify(conversation));
        renderConversation();
        updateConversationsList();
    }
}

function renderConversation() {
    messagesContainer.innerHTML = '';
    
    if (currentConversation.messages.length === 0) {
        renderWelcomeMessage();
        return;
    }
    
    currentConversation.messages.forEach(msg => {
        renderMessage(msg.role, msg.content);
    });
}

function updateConversationsList() {
    conversationsList.innerHTML = '';
    
    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = `conversation-item ${conv.id === currentConversation.id ? 'active' : ''}`;
        item.textContent = conv.title;
        item.addEventListener('click', () => loadConversation(conv.id));
        conversationsList.appendChild(item);
    });
}

// ============================================================================
// STORAGE
// ============================================================================

function saveConversations() {
    // Keep only last 10 conversations for performance
    const existingIndex = conversations.findIndex(c => c.id === currentConversation.id);
    if (existingIndex >= 0) {
        conversations[existingIndex] = currentConversation;
    } else {
        conversations.unshift(currentConversation);
    }
    
    conversations = conversations.slice(0, 10);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
}

function loadConversations() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
        conversations = JSON.parse(stored);
        updateConversationsList();
    }
}

// ============================================================================
// THEME MANAGEMENT
// ============================================================================

function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.classList.toggle('dark-mode');
    localStorage.setItem(THEME_KEY, isDark ? 'dark' : 'light');
    updateThemeIcon();
}

function loadTheme() {
    const theme = localStorage.getItem(THEME_KEY) || 'light';
    if (theme === 'dark') {
        document.documentElement.classList.add('dark-mode');
    }
    updateThemeIcon();
}

function updateThemeIcon() {
    const isDark = document.documentElement.classList.contains('dark-mode');
    themeToggle.textContent = isDark ? '☀️' : '🌙';
}

// ============================================================================
// UI UTILITIES
// ============================================================================

function setLoading(loading) {
    isLoading = loading;
    loadingIndicator.classList.toggle('active', loading);
    sendBtn.classList.toggle('loading', loading);
    sendBtn.disabled = loading;
    messageInput.disabled = loading;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// ============================================================================
// UTILITIES
// ============================================================================

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
