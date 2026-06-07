from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/user', template_folder='templates')

# Import routes only after the blueprint object and other 
# required symbols have been created, so that if routes imports 
# them back from this module, they already exist.
from . import routes