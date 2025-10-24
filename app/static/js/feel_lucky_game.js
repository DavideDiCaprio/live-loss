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
    // ---  Emojis ---
    const emojis = ['🍀', '🍒', '💎', '💰', '🎰', '🔔'];
    // ---  DOM Elements  ---
    const startBtn = document.getElementById('start-game-btn');
    const gameContainer = document.getElementById('game-container');
    const gameBoard = document.getElementById('game-board');
    const gameResult = document.getElementById('game-result');
    const retryBtn = document.getElementById('retry-btn');
    // ---   ---
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
    }
    // ---  ---
    function checkWin(selectedIndex) {
        return __awaiter(this, void 0, void 0, function* () {
            const allFigures = document.querySelectorAll('.figure-btn');
            allFigures.forEach(btn => btn.disabled = true);
            try {
                const response = yield fetch('/api/games/feel-lucky', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ choice: selectedIndex }),
                });
                if (!response.ok) {
                    throw new Error('Game server is down.');
                }
                const data = yield response.json();
                if (data.result === 'win') {
                    gameResult.textContent = 'Wow, great!';
                    gameResult.classList.add('win-message');
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
            retryBtn.classList.remove('hidden');
        });
    }
    startBtn.addEventListener('click', startGame);
    retryBtn.addEventListener('click', startGame);
});
