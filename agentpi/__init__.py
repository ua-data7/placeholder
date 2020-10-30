# -*- coding: utf-8 -*-
import os
import pprint
import click
from pathlib import Path
from dotenv import load_dotenv
from logging.config import dictConfig

from flask import Flask, render_template, request, flash, Markup, jsonify, current_app
from flask.cli import with_appcontext

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate


pp = pprint.PrettyPrinter(indent=4)
# Plugins setup

db = SQLAlchemy()
migrate = Migrate()


## CLI COMMANDS
@click.command(name='start_lis_server')
@click.option('--port')
@click.option('--interface')
@with_appcontext
def start_lis_server(port, interface):
    if(not interface):
        interface = current_app.config['DEFAULT_LIS_NIC']
    if(not port):
        port = current_app.config['DEFAULT_LIS_PORT']
    from agentpi.apps.astm.server import run_server
    run_server(current_app, port, interface)


@click.command(name='send_lis_test')
@with_appcontext
def send_lis_test():
    from agentpi.apps.astm.client import run_client
    run_client(current_app)


@click.command(name='publish_results')
@with_appcontext
def publish_results():
    from agentpi.apps.astm.models import publish_results
    publish_results(current_app)


@click.command(name='show_results')
@with_appcontext
def show_results():
    from agentpi.apps.astm.models import show_results
    show_results(current_app)


def create_app():
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='templates',
        static_folder='static'
    )
    app.config.from_object('config.Config')
    if(('SECRET_KEY' not in app.config) or (app.config['SECRET_KEY'] is None)):
        raise Exception("'SECRET_KEY' undefined!")

    if(('SQLALCHEMY_DATABASE_URI' not in app.config)):
        raise Exception("'SQLALCHEMY_DATABASE_URI' undefined!")

    # Initialize logging
    dictConfig(app.config['LOGGING'])

    # Initialize plugins
    #   Generate models migrations...
    db.init_app(app)
    # Pre-load models for migration stuff... probably need an init phase?
    from agentpi.apps.astm import models as astm_models
    from agentpi.apps.astm.views import home as home_astm
    # initialize migrations...
    migrate.init_app(app, db)

    # Hook in CLI
    app.cli.add_command(start_lis_server)
    app.cli.add_command(send_lis_test)
    app.cli.add_command(publish_results)
    app.cli.add_command(show_results)

    with app.app_context():
        from agentpi.apps.astm import astm_bp
        app.register_blueprint(astm_bp)

        # Create Database Models
        db.create_all()
        return app
