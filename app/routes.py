from app import app
from app.data_handling import handle_raw_data
from flask import request
from flask import abort
from flask import make_response
from flask import jsonify
import json

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/currency_converter', methods=['GET'])
def get_tasks():
    arguments = request.args
    if len(arguments) not in (2, 3):
        abort(400)
    
    try:
        raw_amount = request.args.get('amount')
        raw_input_currency = request.args.get('input_currency')
        raw_output_currency = request.args.get('output_currency')
        output = handle_raw_data(raw_amount,
                                 raw_input_currency,
                                 raw_output_currency)
        return output
    except TypeError:
        abort(400)

@app.errorhandler(400)
def not_found(error):
    error_dict = {'error': 'Wrong parameters'}
    error_output = jsonify(error_dict)
    return make_response(error_output, 400)