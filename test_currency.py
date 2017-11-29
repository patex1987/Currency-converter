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
