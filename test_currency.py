'''
Created on 28. 11. 2017

@author: patex1987
'''
import pytest
import currency_converter
import currency_exceptions
from locale import currency


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
