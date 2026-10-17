from flask import Flask
from .db import query


def create_app():
    """Build and configure the Flask app."""
    app = Flask(__name__)

    @app.route("/health")
    def health():
        """Confirms the app is running and can reach the database."""
        try:
            query("SELECT 1")
            return {"status": "ok", "database": "connected"}
        except Exception as e:
            return {"status": "error", "database": str(e)}, 500
        
    from .routes import bp
    app.register_blueprint(bp)

    return app

    return app

    return app