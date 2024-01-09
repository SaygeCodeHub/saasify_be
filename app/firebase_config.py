import firebase_admin
from firebase_admin import credentials


def initialize_firebase_app():
    cred = credentials.Certificate("saasify-de974-firebase-adminsdk-q7lul-e6555891c4.json")
    firebase_admin.initialize_app(cred)
