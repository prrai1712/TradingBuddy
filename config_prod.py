# Production Configuration Settings
import os

ENV = "production"
# Render requires binding to 0.0.0.0 to handle incoming requests correctly
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 10000))
DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY", "prod-secret-key-change-me-12345")

# Production Host / External URL on Render
RENDER_HOST = os.environ.get("RENDER_EXTERNAL_URL", "https://tradingbuddy.onrender.com")
