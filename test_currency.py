'''
Created on 28. 11. 2017

@author: patex1987
'''
import datetime as dt
import random
import pytest
import currency_converter
import currency_exceptions
import requests


@pytest.fixture
def converter():
    '''
    Returns a CurrencyConverter object
    '''
    return currency_converter.CurrencyConverter()


@pytest.fixture
def converter_without_symbols():
    '''
    Returns a CurrencyConverter object
    '''
    return currency_converter.CurrencyConverter(symbols_file=None)


def test_default_available_currencies(converter):
    """
    Test of the structure, when a single element is inserted
    """
    assert converter.available_currencies is not None


def test_base_rate(converter):
    '''
    Tests the structure of actual rates
    '''
    assert 'last_update' in converter.actual_rates.keys()
    assert 'rates' in converter.actual_rates.keys()
    currency_codes = list(converter.actual_rates['rates'].keys())
    assert currency_codes == [converter.base_currency]


# def test_limit_reached(converter):
#     '''
#     Tests if the CurrencyConverter raises an exception if
#     fixer.io reaches request limit
#     '''
#     with pytest.raises(currency_exceptions.FixerError):
#         for _ in range(100):
#             converter._get_rates_for_base(converter.base_currency)


def test_symbols_presence(converter):
    '''
    Tests if symbols are added to the class
    '''
    assert converter.symbols_map is not None


def test_symbols_presence_wo_symbols(converter_without_symbols):
    '''
    Tests symbols in a converter without symbols
    '''
    assert isinstance(converter_without_symbols.symbols_map, dict)
    assert not list(converter_without_symbols.symbols_map.keys())


def test_symbols_wrong_sep(converter):
    '''
    Tests converter for improper symbol separator
    '''
    with pytest.raises(currency_exceptions.SymbolImportError):
        converter._get_symbols_map(r'txt/symbols.txt', ';')


def test_symbols_map_values(converter):
    '''
    Tests if all values in the symbols map dictionary is 3 letter long
    '''
    symbol_values = list(converter.symbols_map.values())
    currencies = [currency for sublist in symbol_values for currency in sublist]
    currency_length_check = (len(currency) == 3 for currency in currencies)
    assert all(currency_length_check)


def test_input_currency_wrong_inputs(converter):
    '''
    Tests if an improper input currency raises an Exception
    '''
    with pytest.raises(currency_exceptions.CurrencyError):
        assert converter._check_input_currency(raw_input_currency='blahblah')
    with pytest.raises(currency_exceptions.CurrencyError):
        assert converter._check_input_currency(raw_input_currency='££')


def test_input_currency_right_outputs(converter):
    '''
    Tests the output of _check_input_currency
    '''
    with pytest.raises(currency_exceptions.TooManyCurrencies):
        assert converter._check_input_currency(raw_input_currency='$')
    assert converter._check_input_currency(raw_input_currency='EUR') == 'EUR'
    assert converter._check_input_currency(raw_input_currency='CZK') == 'CZK'
    assert converter._check_input_currency(raw_input_currency='€') == 'EUR'
    assert converter._check_input_currency(raw_input_currency='Kč') == 'CZK'


def test_output_currencies_with_none(converter):
    '''
    tests if _check_output_currency returns the right list if None is provided
    as output currency
    '''
    output_currencies = [currency for currency in converter.available_currencies if currency != 'EUR']
    assert converter._check_output_currency('EUR', raw_output_currency=None) == output_currencies


def test_output_currency_wrong_inputs(converter):
    '''
    Tests if an improper output currency raises an Exception
    '''
    with pytest.raises(currency_exceptions.CurrencyError):
        assert converter._check_output_currency('EUR', raw_output_currency='blahblah')
    with pytest.raises(currency_exceptions.CurrencyError):
        assert converter._check_output_currency('EUR', raw_output_currency='££')


def test_output_currency_right_outputs(converter):
    '''
    Tests the output of _check_output_currency
    '''
    dollar_currencies = converter._check_output_currency('EUR', raw_output_currency='$')
    assert 'USD' in dollar_currencies
    assert converter._check_output_currency('EUR', raw_output_currency='CZK') == ['CZK']
    assert converter._check_output_currency('CZK', raw_output_currency='EUR') == ['EUR']


def test_input_amount_number(converter):
    '''
    Tests if a string as input amount raises an error
    '''
    with pytest.raises(currency_exceptions.ConversionError):
        assert converter._check_input_amount(input_amount='text')


def test_conversion_wrong_amount(converter):
    '''
    Tests the conversion result dictionary if wrong input amount is provided
    '''
    conversion_result = converter.convert(input_amount='text',
                                          raw_input_currency='EUR',
                                          raw_output_currency='USD')
    err_str = conversion_result['output']['error']
    test_str = 'Conversion error, check the input parameters'
    assert err_str == test_str


def test_conversion_wrong_input_currency(converter):
    '''
    Tests the conversion result dictionary if wrong input currency is provided
    '''
    conversion_result = converter.convert(input_amount=155.5,
                                          raw_input_currency='££',
                                          raw_output_currency='USD')
    err_str = conversion_result['output']['error']
    test_str = 'Conversion error, the currency can\'t be' + \
               ' recognized'
    assert err_str == test_str


def test_conversion_too_many_input_currencies(converter):
    '''
    Tests the conversion result dictionary if a symbol representing more than
    one currency is provided as input currency
    '''
    conversion_result = converter.convert(input_amount=155.5,
                                          raw_input_currency='$',
                                          raw_output_currency='GBP')
    err_str = conversion_result['output']['error']
    test_str = 'Conversion error, the input symbol represents more ' + \
               'than one currency, try to use 3-letter currency code'
    assert err_str == test_str


def test_conversion_result_input_normal(converter):
    '''
    Tests the conversion result dictionary's input values
    if 3 letter currency code is provided as currency
    '''
    input_amount = 155.5
    input_currency = 'EUR'
    conversion_result = converter.convert(input_amount=input_amount,
                                          raw_input_currency=input_currency,
                                          raw_output_currency='GBP')
    input_test_dict = {}
    input_test_dict['input'] = {}
    input_test_dict['input']['amount'] = input_amount
    input_test_dict['input']['currency'] = input_currency
    assert conversion_result['input'] == input_test_dict['input']


def test_conversion_result_input_symbol(converter):
    '''
    Tests the conversion result dictionary's input values if a symbol is
    provided as currency - symbol with only one currency assigned
    '''
    input_amount = 155.5
    input_currency = '€'
    conversion_result = converter.convert(input_amount=input_amount,
                                          raw_input_currency=input_currency,
                                          raw_output_currency='GBP')
    input_test_dict = {}
    input_test_dict['input'] = {}
    input_test_dict['input']['amount'] = input_amount
    input_test_dict['input']['currency'] = 'EUR'
    assert conversion_result['input'] == input_test_dict['input']


def test_actuality(converter):
    '''
    Tests whether a timestamp fires an update of the conversion table or not
    Note: Fixer.io is updated 4 PM CET
    '''
    original_update = converter.actual_rates['last_update']
    timestamp_prev_day = original_update + dt.timedelta(days=-1)
    converter._check_rates_actuality(timestamp_prev_day)
    new_update = converter.actual_rates['last_update']
    assert new_update == original_update

    timestamp_next_day = original_update + dt.timedelta(days=1)
    converter._check_rates_actuality(timestamp_next_day)
    new_update = converter.actual_rates['last_update']
    assert new_update > original_update


def test_single_conversion_rate_output(converter):
    '''
    Tests whether conversion rate between the same currencies returns 1
    '''
    assert converter._calculate_current_rate('EUR', 'EUR') == 1.0


def test_single_conversion_rate_fixer_io(converter):
    '''
    Tests whether conversion rate calculation returns the same value as
    retrieved from fixer.io
    '''
    input_currency = converter.base_currency
    output_currency = random.choice([currency for currency
                                     in converter.available_currencies
                                     if currency != input_currency])
    expected_output = converter.actual_rates['rates']['EUR'][output_currency]
    returned_output = converter._calculate_current_rate(input_currency,
                                                        output_currency)
    assert returned_output == expected_output


def test_single_conversion_rate_calculated(converter):
    '''
    Tests calculated conversion rate values
    '''
    test_rates = {'AUD': 1.5693,
                  'CZK': 25.524,
                  'DKK': 7.442,
                  'GBP': 0.88115,
                  'HRK': 7.5553,
                  'JPY': 133.7,
                  'PLN': 4.2129,
                  'USD': 1.1885}
    converter.actual_rates['rates']['EUR'] = test_rates

    def check_calculated_rate(input_currency,
                              output_currency,
                              expected_val,
                              threshold=0.001):
        '''
        assertion test help fucntion
        '''
        returned_output = converter._calculate_current_rate(input_currency,
                                                            output_currency)
        assert abs(returned_output - expected_val) < threshold

    test_sets = (('CZK', 'AUD', 0.061483),
                 ('DKK', 'GBP', 0.1184),
                 ('PLN', 'JPY', 31.736),
                 ('HRK', 'USD', 0.15731))
    for test_set in test_sets:
        check_calculated_rate(*test_set)


def test_output_amount(converter):
    '''
    Tests the correctness of the output amount
    '''

    def check_output_amount(input_amount, conversion_rate, expected_amount):
        '''
        Helper function for testing
        '''
        output_amount = converter._calculate_output_amount(input_amount,
                                                           conversion_rate)
        assert output_amount == expected_amount

    test_sets = ((155.12, 1.0, 155.12),
                 (14.85, 0.187653, 2.79),
                 (5, 2, 10),
                 (5, 0.5, 2.50))
    for test_set in test_sets:
        check_output_amount(*test_set)


def test_conversion_result_output_node(converter):
    '''
    Tests the conversion result dictionary's output node
    '''
    def check_conversion_output_node(input_amount,
                                     input_currency,
                                     output_currency,
                                     expected_result):
        '''
        Helper function for testing
        '''
        conversion_result = converter.convert(input_amount,
                                              input_currency,
                                              output_currency)
        conversion_output_currencies = list(conversion_result['output'].keys())
        assert sorted(conversion_output_currencies) == sorted(expected_result)

    eur_outputs = [currency for currency
                   in converter.available_currencies
                   if currency != 'EUR']
    gbp_outputs = [currency for currency
                   in converter.available_currencies
                   if currency != 'GBP']
    dollar_outputs = ['AUD', 'HKD', 'SGD', 'CAD', 'USD', 'NZD', 'MXN']
    aud_dollar_outputs = ['HKD', 'SGD', 'CAD', 'USD', 'NZD', 'MXN']

    test_sets = ((155.5, '€', 'GBP', ['GBP']),
                 (155.5, '€', None, eur_outputs),
                 (155.5, 'GBP', None, gbp_outputs),
                 (155.5, 'GBP', '$', dollar_outputs),
                 (155.5, 'AUD', '$', aud_dollar_outputs))
    for test_set in test_sets:
        check_conversion_output_node(*test_set)


def test_full_conversion_output(converter):
    '''
    Tests the conversion output with fixed rates
    '''
    test_rates = {'AUD': 1.5693,
                  'CZK': 25.524,
                  'DKK': 7.442,
                  'GBP': 0.88115,
                  'HRK': 7.5553,
                  'JPY': 133.7,
                  'PLN': 4.2129,
                  'USD': 1.1885}
    converter.actual_rates['rates']['EUR'] = test_rates

    def check_conversion_output_dict(output_currency,
                                     expected_value):
        '''
        Helper function for testing
        '''
        conversion_result = converter.convert(1.0,
                                              'EUR',
                                              output_currency)
        output_amount = conversion_result['output'][output_currency]
        expected_value = float("{0:.2f}".format(expected_value))
        assert output_amount == expected_value

    test_sets = (('GBP', test_rates['GBP']),
                 ('CZK', test_rates['CZK']),
                 ('HRK', test_rates['HRK']))

    for test_set in test_sets:
        check_conversion_output_dict(*test_set)

def raise_connection_error():
    '''
    Simulates ConnectionError
    '''
    raise requests.exceptions.ConnectionError

# def test_conversion_connection_error(converter):
#     '''
#     Tests the case, when connection can't be established
#     '''
#     print('TEST')
#     raise_connection_error()
#     conversion_result = converter.convert(input_amount=155.5,
#                                           raw_input_currency='EUR',
#                                           raw_output_currency='USD')
#     err_str = conversion_result['output']['error']
#     test_str = 'Connection error!'
#     print(err_str)
#     assert err_str == test_str
