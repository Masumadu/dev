import logging
import os

from loguru import logger
from flask import Flask, jsonify
from flask_mongoengine import MongoEngine
from sqlalchemy.exc import DBAPIError
from app.extensions import db, migrate, ma

from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import HTTPException
from werkzeug.utils import import_string

# load dotenv in the base root
from app.api_spec import spec
from app.core.exceptions.app_exceptions import (
    app_exception_handler,
    AppExceptionCase,
)


APP_ROOT = os.path.join(os.path.dirname(__file__), "..")  # refers to application_top
dotenv_path = os.path.join(APP_ROOT, ".env")

# SWAGGER
SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Python-Flask-REST-Boilerplate"}
)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


def create_app(config="config.DevelopmentConfig"):
    """Construct the core application"""
    app = Flask(__name__, instance_relative_config=False)
    with app.app_context():
        environment = os.getenv("FLASK_ENV")
        cfg = import_string(config)()
        if environment == "production":
            cfg = import_string("config.ProductionConfig")()
        app.config.from_object(cfg)

        # add extensions
        register_extensions(app)
        app.logger.addHandler(InterceptHandler())
        register_blueprints(app)
        register_swagger_definitions(app)
        return app


def register_extensions(flask_app):
    """Register Flask extensions."""
    from app.core.factory import factory

    if flask_app.config["DB_ENGINE"] == "MONGODB":
        me = MongoEngine()
        me.init_app(flask_app)
    elif flask_app.config["DB_ENGINE"] == "POSTGRES":
        db.init_app(flask_app)
        from app import models
        migrate.init_app(flask_app, db)
        with flask_app.app_context():
            db.create_all()
    factory.init_app(flask_app, db)
    ma.init_app(flask_app)

    @flask_app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return app_exception_handler(e)

    @flask_app.errorhandler(DBAPIError)
    def handle_db_exception(e):
        return app_exception_handler(e)

    @flask_app.errorhandler(AppExceptionCase)
    def handle_app_exceptions(e):
        return app_exception_handler(e)

    return None


def register_blueprints(app):
    from .api.api_v1 import api

    """Register Flask blueprints."""
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    api.init_app(app)
    return None


def register_swagger_definitions(app):
    with app.test_request_context():
        for fn_name in app.view_functions:
            if fn_name == "static":
                continue
            print(f"Loading swagger docs for function: {fn_name}")
            view_fn = app.view_functions[fn_name]
            spec.path(view=view_fn)

    @app.route("/static/swagger.json")
    def create_swagger_spec():
        """
        Swagger API definition.
        """
        return jsonify(spec.to_dict())
