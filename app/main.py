import random
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import pages
from app.models.user import User

# .
# .
test_user = User(
    name="Pippo",
    credit=random.randint(50, 500),
    gambling_losses=random.randint(100, 1000)
)

app = FastAPI()

app.state.test_user = test_user

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pages.router)
