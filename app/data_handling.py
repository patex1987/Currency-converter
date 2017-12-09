import currency_exceptions
from converter_class import CurrencyConverter

from flask import jsonify


def handle_raw_data(raw_amount,
                    raw_input_currency,
                    raw_output_currency):
    '''handles conversion from flask requests

    Checks if the `raw_amount` can be converted to float, then sends the
    parameters into CurrencyConverter's convert method. Returns jsonified
    dictionary

    Args:
        raw_amount (str):
        raw_input_currency (str):
        raw_output_currency (str):

    Returns:
        str: jsonified output from `CurrencyConverter.convert`

    '''

    try:
        amount = float(raw_amount)
    except ValueError:
        amount = raw_amount
    converter = CurrencyConverter(symbols_file=r'./txt/symbols.txt',
                                  rates_file='./rates.pickle')
    response = converter.convert(amount,
                                 raw_input_currency,
                                 raw_output_currency)
    json_response = jsonify(response)
    return json_response