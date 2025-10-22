document.addEventListener('DOMContentLoaded', () => {

    // ---  Emojis ---
    const emojis: string[] = ['🍀', '🍒', '💎', '💰', '🎰', '🔔'];

    // ---  DOM Elements  ---
    const startBtn = document.getElementById('start-game-btn') as HTMLButtonElement;
    const gameContainer = document.getElementById('game-container') as HTMLDivElement;
    const gameBoard = document.getElementById('game-board') as HTMLDivElement;
    const gameResult = document.getElementById('game-result') as HTMLDivElement;
    const retryBtn = document.getElementById('retry-btn') as HTMLButtonElement;

    // ---   ---
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
    }

    // ---  ---
    async function checkWin(selectedIndex: number): Promise<void> {
        
        const allFigures = document.querySelectorAll('.figure-btn') as NodeListOf<HTMLButtonElement>;
        allFigures.forEach(btn => btn.disabled = true);

        try {
            const response = await fetch('/api/games/feel-lucky', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ choice: selectedIndex }),
            });

            if (!response.ok) {
                throw new Error('Game server is down.');
            }

            const data: { result: string, bonusIndex: number } = await response.json();

            if (data.result === 'win') {
                gameResult.textContent = 'Wow, great!';
                gameResult.classList.add('win-message');
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

        retryBtn.classList.remove('hidden');
    }

    startBtn.addEventListener('click', startGame);
    retryBtn.addEventListener('click', startGame);
});
