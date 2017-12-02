'''
Created on 28. 11. 2017

@author: patex1987
'''
import pytest
import currency_converter
import currency_exceptions


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
    assert converter_without_symbols.symbols_map is None


def test_symbols_wrong_sep(converter):
    '''
    Tests converter for improper symbol separator
    '''
    with pytest.raises(currency_exceptions.SymbolImportError):
        converter._get_symbols_map(r'txt\symbols.txt', ';')


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
    test_str = 'Conversion error, the input currency can\'t be' + \
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
    test_str = 'Conversion error, the input symbol represents more' + \
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
