import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api

from .db import init_db
from .routes.auth import blp as auth_blp
from .routes.health import blp as health_blp

# Load environment variables from .env if present (safe no-op if missing)
load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False

# Minimal config for OpenAPI/Swagger UI (flask-smorest)
app.config["API_TITLE"] = "User Profile Management API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Flask secret key (also used for JWT signing in app/auth.py)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# CORS: allow local React dev server
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:3000"]}},
    supports_credentials=False,
)

api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)

# Ensure DB tables exist at startup (lightweight, safe for SQLite)
init_db()


@app.errorhandler(404)
def _handle_404(_err):
    return jsonify({"code": 404, "error": "Not Found", "message": "Route not found"}), 404


@app.errorhandler(405)
def _handle_405(_err):
    return jsonify({"code": 405, "error": "Method Not Allowed", "message": "Method not allowed"}), 405
