from flask import Flask
from flask_cors import CORS

def create_app():
    # Correct static settings
    app = Flask(__name__, static_folder="static")

    # Enable CORS
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # ---------------- REGISTER BLUEPRINTS ----------------
    from app.routes.expiry import expiry_bp
    from app.routes.option_price import option_bp
    from app.routes.nifty import nifty_bp
    from app.routes.live_data import live_bp

    app.register_blueprint(expiry_bp)
    app.register_blueprint(option_bp)
    app.register_blueprint(nifty_bp)
    app.register_blueprint(live_bp)

    # ---------------- STATIC ROUTES ----------------
    @app.route("/")
    def root():
        return app.send_static_file("index.html")

    @app.route("/index.html")
    def index_html():
        return app.send_static_file("index.html")

    # favicon fix
    @app.route("/favicon.ico")
    def favicon():
        return app.send_static_file("favicon.ico")

    # Fallback (only if you're building SPA)
    @app.errorhandler(404)
    def page_not_found(e):
        return app.send_static_file("index.html")

    return app
