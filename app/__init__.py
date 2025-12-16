from flask import Flask, send_from_directory
from flask_cors import CORS

def create_app():
    app = Flask(__name__, static_folder="static")

    # Enable CORS
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # ---------------- LANDING PAGE ----------------
    @app.route("/")
    def landing():
        return send_from_directory("static/landing", "landing.html")

    # ---------------- DASHBOARD ----------------
    @app.route("/dashboard")
    def dashboard():
        return app.send_static_file("index.html")

    # ---------------- REGISTER API BLUEPRINTS ----------------
    from app.routes.expiry import expiry_bp
    from app.routes.option_price import option_bp
    from app.routes.nifty import nifty_bp
    from app.routes.live_data import live_bp

    app.register_blueprint(expiry_bp)
    app.register_blueprint(option_bp)
    app.register_blueprint(nifty_bp)
    app.register_blueprint(live_bp)

    # ---------------- FAVICON ----------------
    @app.route("/favicon.ico")
    def favicon():
        return app.send_static_file("favicon.ico")

    # Fallback (only if you're building SPA)
    @app.errorhandler(404)
    def page_not_found(e):
        return app.send_static_file("landing.html")

    return app
