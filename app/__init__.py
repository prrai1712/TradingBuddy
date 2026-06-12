from flask import Flask, send_from_directory
from flask_cors import CORS

def create_app():
    app = Flask(__name__, static_folder="static")

    # Load configuration depending on environment
    import os
    env = os.environ.get("FLASK_ENV", "local")
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if env == "production":
        config_file = os.path.join(root_dir, "config_prod.py")
    else:
        config_file = os.path.join(root_dir, "config_local.py")
        
    if os.path.exists(config_file):
        app.config.from_pyfile(config_file)
    else:
        app.config.from_mapping(
            ENV=env,
            HOST="0.0.0.0" if env == "production" else "127.0.0.1",
            PORT=int(os.environ.get("PORT", 5000)),
            DEBUG=(env != "production"),
            SECRET_KEY=os.environ.get("SECRET_KEY", "default-secret-key-12345"),
            RENDER_HOST="https://tradingbuddy.onrender.com" if env == "production" else ""
        )

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
    from app.routes.full_chain import full_chain_bp
    from app.routes.analysis import analysis_bp

    app.register_blueprint(expiry_bp)
    app.register_blueprint(option_bp)
    app.register_blueprint(nifty_bp)
    app.register_blueprint(live_bp)
    app.register_blueprint(full_chain_bp)
    app.register_blueprint(analysis_bp)
    

    # ---------------- FAVICON ----------------
    @app.route("/favicon.ico")
    def favicon():
        return app.send_static_file("favicon.ico")

    # Fallback (only if you're building SPA)
    @app.errorhandler(404)
    def page_not_found(e):
        return app.send_static_file("landing.html")

    return app
