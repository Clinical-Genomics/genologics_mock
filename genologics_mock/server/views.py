# !/usr/bin/env python

from flask import (
    render_template,
    Blueprint,
    current_app,
    session)

import logging

LOG = logging.getLogger(__name__)

app = current_app
server_bp = Blueprint("server", __name__)


@server_bp.route("/", methods=["GET", "POST"])
def index():
    """Index view."""

    return render_template("index.html", page_id="index")


@server_bp.route("/samples")
def samples():
    """List of all samples"""

    samples = session.get("samples")
    return render_template("samples.html", samples=samples, page_id="samples")


@server_bp.route("/samples/<sample_id>/")
def sample(sample_id):
    """."""

    return render_template(
        "sample.html",
        page_id="sample",
    )
