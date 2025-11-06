"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
document.addEventListener('DOMContentLoaded', () => {
    const currentUserId = 1;
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/realtime/${currentUserId}`);
    // ---  Emojis ---
    const emojis = ['🍀', '🍒', '💎', '💰', '🎰', '🔔'];
    // ---  DOM Elements  ---
    const startBtn = document.getElementById('start-game-btn');
    const gameContainer = document.getElementById('game-container');
    const gameBoard = document.getElementById('game-board');
    const gameResult = document.getElementById('game-result');
    const retryBtn = document.getElementById('retry-btn');
    // Real-Time Chat/Broadcast Elements (You need to add these to index.html)
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatLog = document.getElementById('chat-log');
    // --- ADD THIS FUNCTION ---
    /**
     * Finds the current user on the leaderboard and applies a highlight style.
     */
    function highlightCurrentUser() {
        try {
            // Find the <li> element that has the matching data-userid
            const userRow = document.querySelector(`.leaderboard li[data-userid="${currentUserId}"]`);
            if (userRow) {
                userRow.classList.add('is-current-user');
            }
            else {
                console.warn(`Could not find current user (ID: ${currentUserId}) on the leaderboard.`);
            }
        }
        catch (error) {
            console.error('Error highlighting user:', error);
        }
    }
    // --- WebSocket Event Handlers ---
    ws.onopen = () => {
        console.log(`WebSocket connected for user ${currentUserId}. Ready for real-time updates.`);
        // Send initial connection status
        sendMessage(`User ${currentUserId} has joined the game lobby.`, 'status');
    };
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log('Received Real-Time Update:', data);
            handleRealTimeMessage(data);
        }
        catch (error) {
            console.error('Failed to parse WebSocket message:', event.data, error);
        }
    };
    ws.onclose = () => {
        console.log('WebSocket disconnected.');
    };
    ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
    };
    highlightCurrentUser();
    function handleRealTimeMessage(data) {
        switch (data.type) {
            case 'chat_message':
                if (chatLog && data.message) {
                    const prefix = data.sender_id === currentUserId ? 'You' : `User ${data.sender_id}`;
                    displayChatMessage(`${prefix}: ${data.message}`);
                }
                break;
            case 'leaderboard_update':
                console.log('Leaderboard update received. Triggering UI refresh.');
                displayChatMessage(`[System] Leaderboard updated!`, 'system');
                break;
            case 'status':
                if (chatLog && data.message) {
                    displayChatMessage(`[Status] ${data.message}`, 'system');
                }
                break;
            default:
                console.warn('Unknown real-time message type:', data.type);
        }
    }
    // --- WebSocket Helper ---
    function sendMessage(message, type = 'chat_message') {
        if (ws.readyState === ws.OPEN) {
            const payload = {
                type: type,
                sender_id: currentUserId,
                message: message
            };
            ws.send(JSON.stringify(payload));
        }
        else {
            console.warn('WebSocket not open. Message not sent.');
        }
    }
    // --- Chat UI Helper (for demonstration) ---
    function displayChatMessage(message, style = 'other') {
        if (!chatLog)
            return;
        const p = document.createElement('p');
        p.textContent = message;
        // Simple styling based on message type (for demo)
        if (style === 'system') {
            p.style.color = '#e6c300'; // Gold color for system messages
        }
        else if (style === 'user') {
            p.style.color = '#28a745'; // Green for user's own messages (not used here, server does the echo)
        }
        chatLog.appendChild(p);
        chatLog.scrollTop = chatLog.scrollHeight; // Scroll to bottom
    }
    // --- Game Logic Functions ---
    function startGame() {
        startBtn.classList.add('hidden');
        gameContainer.classList.remove('hidden');
        retryBtn.classList.add('hidden');
        gameResult.textContent = '';
        gameResult.className = '';
        gameBoard.innerHTML = '';
        emojis.forEach((emoji, index) => {
            const figureButton = document.createElement('button');
            figureButton.textContent = emoji;
            figureButton.classList.add('figure-btn');
            figureButton.addEventListener('click', () => {
                checkWin(index);
            });
            gameBoard.appendChild(figureButton);
        });
        // Broadcast that a new game has started
        sendMessage(`User ${currentUserId} is feeling lucky and starting a new round!`, 'status');
    }
    function checkWin(selectedIndex) {
        return __awaiter(this, void 0, void 0, function* () {
            const allFigures = document.querySelectorAll('.figure-btn');
            allFigures.forEach(btn => btn.disabled = true);
            try {
                // Note: This API call still requires an update on the backend to track the user ID 
                // and perform the balance update, which would then trigger the Redis broadcast.
                const response = yield fetch('/api/games/feel-lucky', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    // UPDATED: Send the choice AND the currentUserId
                    body: JSON.stringify({
                        choice: selectedIndex,
                        user_id: currentUserId
                    }),
                });
                if (!response.ok) {
                    throw new Error('Game server is down.');
                }
                const data = yield response.json();
                if (data.result === 'win') {
                    gameResult.textContent = 'Wow, great!';
                    gameResult.classList.add('win-message');
                    // --- ADDED: Reload the page to show new leaderboard balance ---
                    // We wait 1.5 seconds so the user can read the win message
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                    // --- End of added logic ---
                }
                else {
                    gameResult.textContent = 'Not this time...';
                    gameResult.classList.add('lose-message');
                    allFigures[data.bonusIndex].style.borderColor = '#e6c300';
                    allFigures[data.bonusIndex].style.backgroundColor = '#5a4d1d';
                }
            }
            catch (error) {
                console.error('Error playing game:', error);
                gameResult.textContent = 'Error connecting to game...';
                gameResult.classList.add('lose-message');
            }
            // Only show retry button if the game didn't win (since win reloads)
            if (gameResult.classList.contains('lose-message')) {
                retryBtn.classList.remove('hidden');
            }
        });
    }
    // --- Event Listeners ---
    startBtn.addEventListener('click', startGame);
    retryBtn.addEventListener('click', startGame);
    // Listen for the Enter key on the chat input
    chatInput === null || chatInput === void 0 ? void 0 : chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            chatSendBtn === null || chatSendBtn === void 0 ? void 0 : chatSendBtn.click();
        }
    });
    // Listen for the send button click
    chatSendBtn === null || chatSendBtn === void 0 ? void 0 : chatSendBtn.addEventListener('click', () => {
        if (chatInput === null || chatInput === void 0 ? void 0 : chatInput.value.trim()) {
            sendMessage(chatInput.value.trim(), 'chat_message');
            // Show the user's message locally immediately
            displayChatMessage(`You: ${chatInput.value.trim()}`, 'user');
            chatInput.value = ''; // Clear input
        }
    });
});
