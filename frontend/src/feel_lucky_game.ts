document.addEventListener('DOMContentLoaded', () => {

    const currentUserId = 1; 
    
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/realtime/${currentUserId}`);

    // ---  Emojis ---
    const emojis: string[] = ['🍀', '🍒', '💎', '💰', '🎰', '🔔'];

    // ---  DOM Elements  ---
    const startBtn = document.getElementById('start-game-btn') as HTMLButtonElement;
    const gameContainer = document.getElementById('game-container') as HTMLDivElement;
    const gameBoard = document.getElementById('game-board') as HTMLDivElement;
    const gameResult = document.getElementById('game-result') as HTMLDivElement;
    const retryBtn = document.getElementById('retry-btn') as HTMLButtonElement;
    const chatInput = document.getElementById('chat-input') as HTMLInputElement | null;
    const chatSendBtn = document.getElementById('chat-send-btn') as HTMLButtonElement | null;
    const chatLog = document.getElementById('chat-log') as HTMLDivElement | null;

    /**
     * Finds the current user on the leaderboard and applies a highlight style.
     */
    function highlightCurrentUser(): void {
        try {
            const userRow = document.querySelector(`.leaderboard li[data-userid="${currentUserId}"]`);
            
            if (userRow) {
                userRow.classList.add('is-current-user');
            } else {
                console.warn(`Could not find current user (ID: ${currentUserId}) on the leaderboard.`);
            }
        } catch (error) {
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

        } catch (error) {
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

    // --- Real-Time Message Handler ---
    interface RealTimeData {
        type: 'chat_message' | 'leaderboard_update' | 'status' | string;
        sender_id?: number;
        message?: string;

    }

    function handleRealTimeMessage(data: RealTimeData): void {
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
    function sendMessage(message: string, type: 'chat_message' | 'status' = 'chat_message') {
        if (ws.readyState === ws.OPEN) {
            const payload = {
                type: type,
                sender_id: currentUserId,
                message: message
            };
            ws.send(JSON.stringify(payload)); 
        } else {
            console.warn('WebSocket not open. Message not sent.');
        }
    }
    
    // --- Chat UI Helper (for demonstration) ---
    function displayChatMessage(message: string, style: 'user' | 'system' | 'other' = 'other'): void {
        if (!chatLog) return;
        const p = document.createElement('p');
        p.textContent = message;
        if (style === 'system') {
            p.style.color = '#e6c300'; // Gold color for system messages
        } else if (style === 'user') {
            p.style.color = '#28a745'; // Green for user's own messages (not used here, server does the echo)
        }
        chatLog.appendChild(p);
        chatLog.scrollTop = chatLog.scrollHeight; // Scroll to bottom
    }

    // --- Game Logic Functions ---
    
    function startGame(): void {
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

async function checkWin(selectedIndex: number): Promise<void> {
        
        const allFigures = document.querySelectorAll('.figure-btn') as NodeListOf<HTMLButtonElement>;
        allFigures.forEach(btn => btn.disabled = true);

        try {
            const response = await fetch('/api/games/feel-lucky', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    choice: selectedIndex,
                    user_id: currentUserId 
                }),
            });

            if (!response.ok) {
                throw new Error('Game server is down.');
            }

            const data: { result: string, bonusIndex: number } = await response.json();

            if (data.result === 'win') {
                gameResult.textContent = 'Wow, great!';
                gameResult.classList.add('win-message');
                
                // We wait 1.5 seconds so the user can read the win message
                setTimeout(() => {
                    location.reload();
                }, 1500);

            } else {
                gameResult.textContent = 'Not this time...';
                gameResult.classList.add('lose-message');
                
                allFigures[data.bonusIndex].style.borderColor = '#e6c300';
                allFigures[data.bonusIndex].style.backgroundColor = '#5a4d1d';
            }

        } catch (error) {
            console.error('Error playing game:', error);
            gameResult.textContent = 'Error connecting to game...';
            gameResult.classList.add('lose-message');
        }

        // Only show retry button if the game didn't win (since win reloads)
        if (gameResult.classList.contains('lose-message')) {
            retryBtn.classList.remove('hidden');
        }
    }
    
    // --- Event Listeners ---

    startBtn.addEventListener('click', startGame);
    retryBtn.addEventListener('click', startGame);
    
    // Listen for the Enter key on the chat input
    chatInput?.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            chatSendBtn?.click();
        }
    });
    
    // Listen for the send button click
    chatSendBtn?.addEventListener('click', () => {
        if (chatInput?.value.trim()) {
            sendMessage(chatInput.value.trim(), 'chat_message');
            // Show the user's message locally immediately
            displayChatMessage(`You: ${chatInput.value.trim()}`, 'user');
            chatInput.value = ''; // Clear input
        }
    });
});

