# Local Configuration Settings
import os

ENV = "local"
HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", 5000))
DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "local-secret-key-12345")
RENDER_HOST = ""

