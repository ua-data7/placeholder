"""Flask app configuration."""
from os import environ, path
from dotenv import load_dotenv
import platform

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config(object):
    """Set Flask configuration from environment variables."""
    HOSTNAME = platform.node()
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')
    SECRET_KEY = environ.get('SECRET_KEY')
    DEBUG = True if environ.get('DEBUG', 'false').lower() == 'true' else False

    DEFAULT_LIS_NIC = environ.get('DEFAULT_LIS_NIC')
    DEFAULT_LIS_PORT = environ.get('DEFAULT_LIS_PORT')

    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Assets
    LESS_BIN = environ.get('LESS_BIN')
    ASSETS_DEBUG = environ.get('ASSETS_DEBUG')
    ASSETS_AUTO_BUILD = True
    LESS_RUN_IN_DEBUG = environ.get('LESS_RUN_IN_DEBUG')

    # Static Assets
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    COMPRESSOR_DEBUG = environ.get('COMPRESSOR_DEBUG')

    # AWS UPLINK
    SARS_UPLINK_API_URL = environ.get('SARS_UPLINK_API_URL')
    SARS_UPLINK_API_KEY = environ.get('SARS_UPLINK_API_KEY')

    TEST_UPLINK_API_URL = environ.get('TEST_UPLINK_API_URL')
    TEST_UPLINK_API_KEY = environ.get('TEST_UPLINK_API_KEY')

    DISABLE_UPLINK = True if environ.get('DISABLE_UPLINK', 'false').lower() == 'true' else False
    DISABLE_DATABASE = True if environ.get('DISABLE_DATABASE', 'false').lower() == 'true' else False

    SLACK_WEBHOOK = environ.get('SLACK_WEBHOOK', '')
    SLACK_CHANNEL_ENABLED = environ.get('SLACK_CHANNEL_ENABLED', False)

    LOGGING = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            },
            # 'file': {
            #     'level': 'INFO',
            #     'class': 'logging.FileHandler',
            #     'filename': '/tmp/sofia2-logging.log'
            # }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', ] # 'file'
        }
    }
