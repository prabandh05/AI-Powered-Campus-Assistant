document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const welcomeView = document.getElementById('welcome-view');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const showContextCheckbox = document.getElementById('show-context');
    const newChatButton = document.getElementById('new-chat');
    const historyList = document.getElementById('history-list');
    const openSidebarBtn = document.getElementById('open-sidebar');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const sidebar = document.getElementById('sidebar');

    const API_URL = 'http://localhost:8000';

    let isThinking = false;

    // --- Sidebar & Mobile ---

    openSidebarBtn?.addEventListener('click', () => {
        sidebar.classList.add('active');
    });

    toggleSidebarBtn?.addEventListener('click', () => {
        sidebar.classList.remove('active');
    });

    // --- Input Handling ---

    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
        sendButton.disabled = userInput.value.trim() === '' || isThinking;
    });

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendButton.disabled) {
                handleSendMessage();
            }
        }
    });

    // --- Chat Logic ---

    async function handleSendMessage() {
        const message = userInput.value.trim();
        if (!message || isThinking) return;

        // UI Updates
        if (welcomeView) welcomeView.style.display = 'none';
        appendMessage('user', message);
        userInput.value = '';
        userInput.style.height = 'auto';
        sendButton.disabled = true;
        isThinking = true;

        const loadingBubble = appendLoadingBubble();
        scrollToBottom();

        try {
            const response = await fetch(`${API_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    show_context: showContextCheckbox.checked
                })
            });

            if (!response.ok) throw new Error('Failed to fetch response');

            const data = await response.json();
            
            loadingBubble.remove();
            appendMessage('assistant', data.answer, data.context);
            saveToHistory(message);
        } catch (error) {
            console.error(error);
            loadingBubble.remove();
            appendMessage('assistant', 'Sorry, I encountered an error connecting to the campus assistant backend. Please ensure the server is running.', null, true);
        } finally {
            isThinking = false;
            sendButton.disabled = userInput.value.trim() === '';
            scrollToBottom();
        }
    }

    function appendMessage(role, text, context = null, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex flex-col animate-fade-in ${role === 'user' ? 'items-end' : 'items-start'}`;

        const innerHTML = `
            <div class="flex items-start gap-4 max-w-[85%] lg:max-w-[75%] ${role === 'user' ? 'flex-row-reverse' : ''}">
                <div class="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${role === 'user' ? 'bg-indigo-600' : 'bg-primary-600'}">
                    <i data-lucide="${role === 'user' ? 'user' : 'bot'}" class="w-5 h-5 text-white"></i>
                </div>
                <div class="space-y-2">
                    <div class="p-4 rounded-2xl ${role === 'user' ? 'bg-[#1f2833] text-white border border-gray-700' : 'bg-transparent text-gray-200'}">
                        <div class="prose prose-invert max-w-none">
                            ${formatText(text)}
                        </div>
                    </div>
                    ${context ? `
                        <details class="text-xs text-gray-500 border border-gray-800 rounded-lg overflow-hidden group">
                            <summary class="p-2 cursor-pointer hover:bg-gray-800 flex items-center gap-2 list-none">
                                <i data-lucide="info" class="w-3 h-3"></i>
                                View Retrieved Context
                            </summary>
                            <div class="p-3 bg-[#0b0c10] border-t border-gray-800 font-mono leading-tight whitespace-pre-wrap">
                                ${context}
                            </div>
                        </details>
                    ` : ''}
                </div>
            </div>
        `;

        messageDiv.innerHTML = innerHTML;
        chatMessages.appendChild(messageDiv);
        lucide.createIcons();
        scrollToBottom();
    }

    function appendLoadingBubble() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'flex items-start gap-4 assistant-message animate-fade-in';
        loadingDiv.innerHTML = `
            <div class="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center bg-primary-600">
                <i data-lucide="bot" class="w-5 h-5 text-white"></i>
            </div>
            <div class="loading-dots p-4">
                <span></span><span></span><span></span>
            </div>
        `;
        chatMessages.appendChild(loadingDiv);
        lucide.createIcons();
        return loadingDiv;
    }

    function formatText(text) {
        // Simple markdown-ish formatting
        return text
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- History Management ---

    function saveToHistory(query) {
        const history = JSON.parse(localStorage.getItem('campus_ai_history') || '[]');
        if (!history.includes(query)) {
            history.unshift(query);
            localStorage.setItem('campus_ai_history', JSON.stringify(history.slice(0, 10)));
            renderHistory();
        }
    }

    function renderHistory() {
        if (!historyList) return;
        const history = JSON.parse(localStorage.getItem('campus_ai_history') || '[]');
        historyList.innerHTML = history.map(item => `
            <button class="w-full text-left px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all truncate">
                ${item}
            </button>
        `).join('');
    }

    // --- Event Listeners ---

    sendButton.addEventListener('click', handleSendMessage);

    newChatButton?.addEventListener('click', () => {
        chatMessages.innerHTML = '';
        if (welcomeView) welcomeView.style.display = 'flex';
        chatMessages.appendChild(welcomeView);
    });

    // Suggestions click
    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', () => {
            const text = card.querySelector('p:last-child').textContent;
            userInput.value = text;
            userInput.style.height = 'auto';
            userInput.style.height = userInput.scrollHeight + 'px';
            sendButton.disabled = false;
            handleSendMessage();
        });
    });

    renderHistory();
});
