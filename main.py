from utils import greet_user
from models import Person
from async_tasks import fetch_data

import asyncio

def run_app():
    user = Person("Tanzeela", 25)
    greet_user(user)
    asyncio.run(fetch_data())

if __name__ == "__main__":
    run_app()
