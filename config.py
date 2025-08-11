import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:kridl@localhost:5432/brms'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
