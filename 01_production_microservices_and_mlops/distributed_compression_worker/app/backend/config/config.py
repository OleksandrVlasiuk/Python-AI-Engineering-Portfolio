from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

FRONTEND_URL = os.environ.get("FRONTEND_URL")

MAX_LENGTH = os.environ.get("MAX_LENGTH")

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.environ.get("JWT_REFRESH_SECRET_KEY")
JWT_VERIFICATION_SECRET_KEY = os.environ.get("JWT_VERIFICATION_SECRET_KEY")

TIME_BY_LENGTH = {
    15000: 301,
    14500: 291,
    14000: 268,
    13500: 260,
    13000: 245,
    12500: 211,
    12000: 181,
    11500: 180,
    11000: 171,
    10500: 165,
    10000: 157,
    9500: 148,
    9000: 137,
    8500: 107,
    8000: 90,
    7500: 69,
    7000: 62,
    6500: 56,
    6000: 38,
    5500: 42,
    5000: 37,
    4500: 30,
    4000: 24,
    3500: 13,
    3000: 10,
    2500: 4,
    2000: 0,
    1500: 0,
    1000: 0,
    500: 0,
}

