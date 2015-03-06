import os

# for session to be usable
SECRET_KEY = os.environ.get('SECRET_KEY')

# location of DB
# SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# Gmail OAuth info
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_SECRET')
GMAIL_AUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
