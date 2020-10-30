
from flask import Blueprint
from flask_login import login_required


# Blueprint Configuration
astm_bp = Blueprint(
    'astm_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)
