import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker


load_dotenv()
URL_DATABASE_TEST = os.getenv("URL_DATABASE_TEST")

if not URL_DATABASE_TEST:
    raise RuntimeError("URL_DATABASE_TEST is not set")

if make_url(URL_DATABASE_TEST).database != "QuizApp_test":
    raise RuntimeError("Tests may only run against the QuizApp_test database")

test_engine = create_engine(URL_DATABASE_TEST)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)
