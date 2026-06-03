import os

DATABASE_URI = os.getenv("DATABASE_URL")

if not DATABASE_URI:
    DATABASE_URI = (
        "postgresql://postgres:12345@localhost:5432/smart_parking"
    )