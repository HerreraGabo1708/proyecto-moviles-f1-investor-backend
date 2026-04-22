import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY              = os.getenv('SECRET_KEY', 'dev-secret')
    JWT_SECRET_KEY          = os.getenv('JWT_SECRET_KEY', 'jwt-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'mysql+pymysql://root:@localhost/f1_investment_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES       = 86400   # 24 horas
