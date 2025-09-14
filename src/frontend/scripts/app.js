// App state
let state = {
    currentChatId: null,
    messages: [],
    chats: [],
    files: [],
    thinking: false
};

// API base URL
const API_BASE = 'http://localhost:8080';

// DOM elements
const elements = {
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    fileList: document.getElementById('fileList'),
    chatMessages: document.getElementById('chatMessages'),
    messageInput: document.getElementById('messageInput'),
    sendButton: document.getElementById('sendButton'),
    newChatBtn: document.getElementById('newChatBtn'),
    chatsList: document.getElementById('chatsList'),
    connectionStatus: document.getElementById('connectionStatus'),
    loadingIndicator: document.getElementById('loadingIndicator')
};

// API functions
const api = {
    async request(method, endpoint, data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            if (data && method !== 'GET') {
                if (data instanceof FormData) {
                    delete options.headers['Content-Type'];
                    options.body = data;
                } else {
                    options.body = JSON.stringify(data);
                }
            }

            const response = await fetch(`${API_BASE}${endpoint}`, options);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    async healthCheck() {
        try {
            const response = await fetch(`${API_BASE}/docs`);
            return response.ok;
        } catch {
            return false;
        }
    },

    async getChats() {
        return await this.request('GET', '/chats');
    },

    async createChat(name) {
        return await this.request('POST', `/chat?name=${encodeURIComponent(name)}`);
    },

    async deleteChat(chatId) {
        return await this.request('DELETE', `/chat/${chatId}`);
    },

    async getMessages(chatId) {
        return await this.request('GET', `/chat/${chatId}/messages`);
    },

    async sendMessage(chatId, message) {
        return await this.request('POST', `/chat/${chatId}/message`, { message });
    },

    async uploadFile(chatId, file) {
        const formData = new FormData();
        formData.append('file', file);
        return await this.request('POST', `/chat/${chatId}/upload`, formData);
    },

    async getFiles(chatId) {
        return await this.request('GET', `/chat/${chatId}/documents`);
    }
};

// UI functions
const ui = {
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = `Error: ${message}`;
        elements.chatMessages.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
        this.scrollToBottom();
    },

    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success';
        successDiv.textContent = message;
        elements.fileList.appendChild(successDiv);
        setTimeout(() => successDiv.remove(), 3000);
    },

    updateConnectionStatus(connected) {
        if (connected) {
            elements.connectionStatus.innerHTML = '<span style="color: #28a745;">● Connected</span>';
        } else {
            elements.connectionStatus.innerHTML = '<span style="color: #dc3545;">● Disconnected</span>';
        }
    },

    scrollToBottom() {
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    },

    autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    },

    renderMessages() {
        elements.chatMessages.innerHTML = '';
        
        if (!state.currentChatId) {
            elements.chatMessages.innerHTML = `
                <div class="welcome-screen">
                    <h3>Welcome to ChatDocs</h3>
                    <p>Create or select a chat to start asking questions about your documents</p>
                </div>
            `;
            return;
        }

        if (state.messages.length === 0) {
            elements.chatMessages.innerHTML = `
                <div class="welcome-screen">
                    <h3>Start chatting!</h3>
                    <p>Upload some documents and ask questions about them</p>
                </div>
            `;
            return;
        }

        state.messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${msg.role}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = msg.content;
            
            messageDiv.appendChild(contentDiv);
            
            if (msg.sources && msg.sources.length > 0) {
                const sourcesDiv = document.createElement('div');
                sourcesDiv.className = 'sources';
                sourcesDiv.innerHTML = `
                    <span class="sources-toggle">📄 ${msg.sources.length} source(s)</span>
                    <div class="sources-list">
                        ${msg.sources.map(src => `• ${src}`).join('<br>')}
                    </div>
                `;
                
                sourcesDiv.querySelector('.sources-toggle').addEventListener('click', () => {
                    sourcesDiv.querySelector('.sources-list').classList.toggle('open');
                });
                
                messageDiv.appendChild(sourcesDiv);
            }
            
            elements.chatMessages.appendChild(messageDiv);
        });

        if (state.thinking) {
            const thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'message thinking';
            thinkingDiv.innerHTML = '<div class="message-content">Thinking...</div>';
            elements.chatMessages.appendChild(thinkingDiv);
        }

        this.scrollToBottom();
    },

    renderChats() {
        elements.chatsList.innerHTML = '';
        
        if (state.chats.length === 0) {
            elements.chatsList.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">No chats yet</p>';
            return;
        }
        
        state.chats.forEach(chat => {
            const chatDiv = document.createElement('div');
            chatDiv.className = `chat-item ${chat.id === state.currentChatId ? 'active' : ''}`;
            
            chatDiv.innerHTML = `
                <span class="chat-name">${chat.name}</span>
                <button class="delete-chat">✕</button>
            `;
            
            chatDiv.addEventListener('click', (e) => {
                if (!e.target.classList.contains('delete-chat')) {
                    app.selectChat(chat.id);
                }
            });
            
            chatDiv.querySelector('.delete-chat').addEventListener('click', (e) => {
                e.stopPropagation();
                app.deleteChat(chat.id);
            });
            
            elements.chatsList.appendChild(chatDiv);
        });
    },

    renderFiles() {
        elements.fileList.innerHTML = '';
        
        if (!state.currentChatId) {
            elements.fileList.innerHTML = '<p style="color: #666; text-align: center;">Select a chat first</p>';
            return;
        }

        if (state.files.length === 0) {
            elements.fileList.innerHTML = '<p style="color: #666; text-align: center;">No files uploaded</p>';
            return;
        }

        state.files.forEach(file => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-item';
            
            const icon = {
                'pdf': '📄',
                'txt': '📝', 
                'md': '📋'
            }[file.file_type] || '📄';
            
            fileDiv.innerHTML = `
                <span class="file-icon">${icon}</span>
                <span>${file.filename}</span>
            `;
            
            elements.fileList.appendChild(fileDiv);
        });
    }
};

// Main app functions
const app = {
    async init() {
        console.log('Initializing ChatDocs...');
        await this.checkConnection();
        await this.loadChats();
        this.setupEventListeners();
        ui.renderMessages();
        ui.renderChats();
        ui.renderFiles();
        console.log('ChatDocs initialized successfully');
    },

    async checkConnection() {
        const connected = await api.healthCheck();
        ui.updateConnectionStatus(connected);
        
        if (!connected) {
            ui.showError('Cannot connect to backend. Please start the backend server.');
        }
        
        return connected;
    },

    async loadChats() {
        try {
            state.chats = await api.getChats();
            ui.renderChats();
        } catch (error) {
            console.error('Failed to load chats:', error);
            ui.showError('Failed to load chats');
        }
    },

    async createChat() {
        try {
            const name = `Chat ${state.chats.length + 1}`;
            const newChat = await api.createChat(name);
            state.currentChatId = newChat.id;
            state.messages = [];
            state.files = [];
            await this.loadChats();
            ui.renderMessages();
            ui.renderFiles();
        } catch (error) {
            console.error('Failed to create chat:', error);
            ui.showError('Failed to create chat');
        }
    },

    async deleteChat(chatId) {
        if (!confirm('Are you sure you want to delete this chat?')) return;
        
        try {
            await api.deleteChat(chatId);
            if (state.currentChatId === chatId) {
                state.currentChatId = null;
                state.messages = [];
                state.files = [];
            }
            await this.loadChats();
            ui.renderMessages();
            ui.renderFiles();
        } catch (error) {
            console.error('Failed to delete chat:', error);
            ui.showError('Failed to delete chat');
        }
    },

    async selectChat(chatId) {
        state.currentChatId = chatId;
        try {
            state.messages = await api.getMessages(chatId);
            state.files = await api.getFiles(chatId);
            ui.renderMessages();
            ui.renderChats();
            ui.renderFiles();
        } catch (error) {
            console.error('Failed to load chat:', error);
            ui.showError('Failed to load chat');
        }
    },

    async sendMessage() {
        const message = elements.messageInput.value.trim();
        if (!message || !state.currentChatId) return;

        // Add user message immediately
        state.messages.push({
            role: 'user',
            content: message
        });

        elements.messageInput.value = '';
        ui.autoResize(elements.messageInput);
        state.thinking = true;
        ui.renderMessages();

        try {
            const response = await api.sendMessage(state.currentChatId, message);
            state.thinking = false;
            
            state.messages.push({
                role: 'assistant',
                content: response.response,
                sources: response.sources || []
            });
            
            ui.renderMessages();
        } catch (error) {
            console.error('Failed to send message:', error);
            state.thinking = false;
            state.messages.push({
                role: 'assistant',
                content: `Error: ${error.message}`
            });
            ui.renderMessages();
        }
    },

    async uploadFile(file) {
        if (!state.currentChatId) {
            ui.showError('Please select a chat first');
            return;
        }

        // Validate file type
        const allowedTypes = ['pdf', 'txt', 'md'];
        const fileType = file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileType)) {
            ui.showError('Unsupported file type. Please upload PDF, TXT, or MD files.');
            return;
        }

        try {
            await api.uploadFile(state.currentChatId, file);
            ui.showSuccess(`Uploaded: ${file.name}`);
            state.files = await api.getFiles(state.currentChatId);
            ui.renderFiles();
        } catch (error) {
            console.error('Failed to upload file:', error);
            ui.showError(`Upload failed: ${error.message}`);
        }
    },

    setupEventListeners() {
        // File upload
        elements.uploadArea.addEventListener('click', () => elements.fileInput.click());
        elements.fileInput.addEventListener('change', (e) => {
            if (e.target.files[0]) {
                this.uploadFile(e.target.files[0]);
                e.target.value = ''; // Clear input
            }
        });

        // Drag & drop
        elements.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            elements.uploadArea.classList.add('drag-over');
        });

        elements.uploadArea.addEventListener('dragleave', () => {
            elements.uploadArea.classList.remove('drag-over');
        });

        elements.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            elements.uploadArea.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file) this.uploadFile(file);
        });

        // Message input
        elements.messageInput.addEventListener('input', (e) => ui.autoResize(e.target));
        elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        elements.sendButton.addEventListener('click', () => this.sendMessage());

        // New chat
        elements.newChatBtn.addEventListener('click', () => this.createChat());

        // Auto-scroll on new messages
        const observer = new MutationObserver(() => {
            if (elements.chatMessages.children.length > 0) {
                ui.scrollToBottom();
            }
        });
        observer.observe(elements.chatMessages, { childList: true });

        // Check connection periodically
        setInterval(async () => {
            const connected = await api.healthCheck();
            ui.updateConnectionStatus(connected);
        }, 30000); // Every 30 seconds
    }
};

// Initialize app when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, starting ChatDocs...');
    app.init();
});