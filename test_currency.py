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
    assert len(converter.available_currencies) > 0


def test_default_rates(converter):
    '''
    Tests the structure of actual rates
    '''
    assert 'last_update' in converter.actual_rates.keys()
    assert 'rates' in converter.actual_rates.keys()
    currency_codes = list(converter.actual_rates['rates'].keys())
    assert currency_codes
    print(currency_codes)
    assert all((len(code) == 3 for code in currency_codes)) is True

def test_limit_reached(converter):
    '''
    Tests if the CurrencyConverter raises an exception if
    fixer.io reaches request limit
    '''
    with pytest.raises(currency_exceptions.FixerError) as err_inf:
        for _ in range(100):
            converter._get_rates_for_base('EUR')
