from flask import render_template
from . import core_bp
from flask import jsonify

@core_bp.route('/', methods=['GET'])
def home():
    return render_template('core/home.html')

@core_bp.route('/about', methods=['GET'])
def about():
    return render_template('core/about.html')


@core_bp.route('/api/liveness', methods=['GET'])
def liveness():
    return jsonify({"status": "alive"})