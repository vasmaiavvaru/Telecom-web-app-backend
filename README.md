# Telecom-web-app-backend

This is the backend for the telecom web app. It is a REST API that is used to communicate with the frontend. It is written in Python using the Flask framework.

## Installation
- Install Python 3.9
- Install poetry `pip install poetry`
- Install dependencies `poetry install`
- Install asyncmy `pip install asyncmy`
- Setup pre-commit hooks `pre-commit install`
- Run migrations `alembic upgrade head`
- Inject initial data `python app/initial_data.py`
- Change `.env.example` to `.env` and fill in the values
- Run the app `python -m app`
