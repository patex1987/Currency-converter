'''
Created on 28. 11. 2017

@author: patex1987

Tests for the api, using pytest-flask
'''
import json
import pytest
from flask_app import app


@pytest.fixture
def client(request):
    test_client = app.test_client()

    return test_client


def json_of_response(response):
    '''
    json decoding
    '''
    return json.loads(response.data.decode('utf8'))


def test_basic_converter_response(client):
    '''
    tests if `/currency_converter` returns error 400
    '''
    response = client.get('/currency_converter')
    response_json = json_of_response(response)
    assert response.status_code == 400
    assert response_json['error'] == 'Wrong parameters'


def test_converter_too_much_parameters(client):
    '''
    tests the response if an incorrect number of arguments is in the
    request
    '''
    response = client.get('/currency_converter?amount=100')
    response_json = json_of_response(response)
    assert response.status_code == 400
    assert response_json['error'] == 'Wrong parameters'


def test_converter_text_amount(client):
    '''
    tests the response if a text is provided as amount
    '''
    base_uri = '/currency_converter?amount={0}&input_currency={1}' + \
               '&output_currency={2}'
    uri_text = base_uri.format('blahblah', 'EUR', 'GBP')
    response = client.get(uri_text)
    response_json = json_of_response(response)
    expected_output = 'Conversion error, check the input parameters'
    assert response_json['output']['error'] == expected_output


def test_converter_unknown_currency(client):
    '''
    tests the response if an unknown currency is provided
    '''
    base_uri = '/currency_converter?amount={0}&input_currency={1}' + \
               '&output_currency={2}'
    uri_text = base_uri.format('100', 'unknown', 'GBP')
    response = client.get(uri_text)
    response_json = json_of_response(response)
    expected_output = 'Conversion error, the currency can\'t be recognized'
    assert response_json['output']['error'] == expected_output


def test_converter_toomuch_input_currency(client):
    '''
    tests the response if a symbol with more than one currencies is
    provided as input currency
    '''
    base_uri = '/currency_converter?amount={0}&input_currency={1}' + \
               '&output_currency={2}'
    uri_text = base_uri.format('100', '$', 'GBP')
    response = client.get(uri_text)
    response_json = json_of_response(response)
    expected_output = 'Conversion error, the input symbol represents more ' + \
                      'than one currency, try to use 3-letter currency code'
    assert response_json['output']['error'] == expected_output
