import firebase_admin
from firebase_admin import credentials, auth
from app.core.config import settings

firebase_app = None

def initialize_firebase():
    print(" Initializing Firebase Admin SDK...")
    global firebase_app
    if not firebase_admin._apps:
        print(" Firebase initialized")
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_app = firebase_admin.initialize_app(cred)
    else:
        print(" Firebase already initialized")
    return firebase_app
    