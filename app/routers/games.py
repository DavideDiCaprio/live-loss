import random
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.user import User
from app.models.game import GameResult, Figure

router = APIRouter()

# Possible figures and their bonus ranges
POSSIBLE_FIGURES = {
    "Cherry": (5, 15),
    "Lemon": (10, 25),
    "Orange": (15, 30),
    "Bell": (20, 40),
    "Diamond": (50, 100),
    "Seven": (100, 200)
}

@router.post("/play/get-bonus", response_model=GameResult)
async def play_get_bonus(request: Request):
    """
    Simulates a round of the 'Get Bonus' game.
    Generates 6 random figures and calculates the total bonus.
    """
    user: User = request.app.state.test_user
    
    selected_figures = []
    total_bonus = 0

    figure_names = list(POSSIBLE_FIGURES.keys())

    for _ in range(6):
        figure_name = random.choice(figure_names)
        min_bonus, max_bonus = POSSIBLE_FIGURES[figure_name]
        bonus = random.randint(min_bonus, max_bonus)
        
        selected_figures.append(Figure(name=figure_name, bonus=bonus))
        total_bonus += bonus

    # Update user's credit
    user.credit += total_bonus
    
    return GameResult(
        figures=selected_figures,
        total_bonus=total_bonus,
        new_credit=user.credit
    )
