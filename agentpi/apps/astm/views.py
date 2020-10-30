import pprint

from flask import Blueprint, jsonify, request, abort, current_app
from flask.cli import with_appcontext

from jinja2 import TemplateNotFound

from . import astm_bp


pp = pprint.PrettyPrinter(indent=4)


@astm_bp.route('/api/test_result', methods = ['GET', 'POST'])
def home():
    if(request.method == 'GET'):
        data = "hello world"
        return jsonify({'data': data})
    elif(request.method == 'POST'):
        key = request.headers.get('x-api-key')
        if key == current_app.config['TEST_UPLINK_API_KEY']:
            pp.pprint(request.get_json())
            return('OK')
        else:
            abort(401)

