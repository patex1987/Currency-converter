'''
Created on 28. 11. 2017

@author: patex1987
'''
import pytest
import currency_converter


@pytest.fixture
def converter():
    '''Returns a Wallet instance with a balance of 20'''
    return currency_converter.CurrencyConverter()


def test_default_available_currencies(converter):
    """
    Test of the structure, when a single element is inserted
    """
    assert converter.available_currencies is not None
    assert len(converter.available_currencies) > 0


def test_default_rates(converter):
    '''
    Tests the structure of actual rates
    '''
    assert 'last_update' in converter.actual_rates.keys()
    assert 'rates' in converter.actual_rates.keys()
    currency_codes = converter.actual_rates['rates'].keys()
    print(currency_codes)
    assert all((len(code) for code in currency_codes)) is True
