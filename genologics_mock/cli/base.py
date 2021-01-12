
#!/usr/bin/env python
import logging

import click

from flask.cli import FlaskGroup, with_appcontext
from flask import current_app

# commands
from genologics_mock.server import create_app


LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)


@click.group(
    cls=FlaskGroup,
    create_app=create_app,
    add_default_commands=True,
    invoke_without_command=False,
    add_version_option=False)

@with_appcontext
def cli():
    """ Main entry point """
    pass

@cli.command()
@with_appcontext
def name():
    """Returns the app name, for testing purposes, mostly"""
    click.echo(current_app.name)
    return current_app.name


cli.add_command(name)