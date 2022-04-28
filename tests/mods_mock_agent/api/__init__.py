"""This module defines flask app factory method"""

import logging
from flask import Flask
from routes.public import mods_mock_agent_bp
from routes.admin import admin_api

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s %(asctime)s [%(name)s]: %(message)s",
    handlers=[logging.StreamHandler()],
)

logging.getLogger("werkzeug").setLevel(logging.ERROR)


def create_app(config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    if config is not None:
        # load the test config if passed in
        app.config.from_mapping(config)
    else:
        app.config.from_pyfile("config.py", silent=False)

    # Register Blueprints
    app.register_blueprint(mods_mock_agent_bp, url_prefix="/")
    app.register_blueprint(admin_api, url_prefix="/admin")

    return app
