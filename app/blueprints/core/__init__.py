from flask import Blueprint

core_bp = Blueprint('core', __name__, template_folder='templates')

# Import routes only after the blueprint object and other 
# required symbols have been created, so that if routes imports 
# them back from this module, they already exist.
from . import routes