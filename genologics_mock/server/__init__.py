
import logging

from flask import Flask

from genologics_mock.server.views import server_bp

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'HEJ'
    app.config['DEBUG'] = 0

    app.register_blueprint(server_bp)

    return app


