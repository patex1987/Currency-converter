'''
Created on 27. 11. 2017

@author: patex1987
'''

from collections import defaultdict
import datetime as dt
import requests
import currency_exceptions as exceptions


class CurrencyConverter(object):
    '''
    This class handles all the currency conversion related operations
    '''

    def __init__(self, symbols_file=None, symbols_sep='\t'):
        '''
        Constructor
        '''
        self.api_base_url = 'https://api.fixer.io'
        self.base_currency = 'EUR'
        self.available_currencies = None
        self.actual_rates = self._get_actual_rates()
        self.symbols_map = None
        if symbols_file is not None:
            self.symbols_map = self._get_symbols_map(symbols_file, symbols_sep)

    def convert(self,
                input_amount,
                input_currency,
                output_currency=None):
        '''
        converts the input amount into a structured output
        output currency can be a single currency or all available currencies
        '''
        self._check_rates_actuality()
        output_currencies = self._get_current_outputs(input_currency,
                                                      output_currency)
        output_amounts = self._get_all_conversions(input_amount,
                                                   input_currency,
                                                   output_currencies)
        return output_amounts

    def _convert_single_currency(self,
                                 input_amount,
                                 input_currency,
                                 output_currency):
        '''
        Converts the provided input amount of money into the desired output
        amount
        '''
        actual_conversion_rate = self._calculate_current_rate(input_currency,
                                                              output_currency)
        output_amount = self._calculate_output_amount(input_amount,
                                                      actual_conversion_rate)
        return output_amount

    def _get_actual_rates(self):
        '''
        Retrieves the actual currency conversion rates from fixer.io
        '''
        actual_rates = {}
        actual_rates['last_update'] = None
        actual_rates['rates'] = {}
        act_currency = self.base_currency
        try:
            act_rates = self._get_rates_for_base(act_currency)
            actual_rates['rates'][act_currency] = act_rates
            actual_rates['last_update'] = dt.datetime.now()
            self.available_currencies = [self.base_currency] + list(act_rates.keys())
            return actual_rates
        except exceptions.FixerError:
            pass
        if not hasattr(self, 'actual_rates'):
            return actual_rates
        if actual_rates['last_update'] is None:
            return self.actual_rates

    def _get_symbols_map(self, file_name, separator):
        '''
        gets currency symbols mapping
        '''
        symbol_map = defaultdict(list)
        with open(file_name) as input_file:
            for line in input_file:
                data = line.strip().split(separator)
                if len(data) != 2:
                    raise exceptions.SymbolImportError
                symbol_encoded = bytes(data[0], encoding='utf-8')
                currency = data[1]
                symbol_map[symbol_encoded].append(currency)
        return symbol_map

    def _get_current_outputs(self, input_currency, output_currency):
        '''
        returns a list of possible output currencies for the selected input
        currency
        '''

    def _get_all_conversions(self,
                             input_amount,
                             input_currency,
                             output_currencies):
        output_conversions = {}
        if not output_currencies:
            return {}
        for currency in output_currencies:
            output_amount = self._convert_single_currency(input_amount,
                                                          input_currency,
                                                          currency)
            output_conversions[currency] = output_amount
        return output_conversions

    def _check_rates_actuality(self):
        '''
        Check whether the actual_rates dictionary holds the newest currency
        rates
        '''

    def _calculate_current_rate(self, input_currency, output_currency):
        '''
        calculates the currency conversion rate needed to convert from input to
        output conversion. EUR is the basis currency
        '''

    def _calculate_output_amount(self, input_amount, conversion_rate):
        '''
        Returns the output amount
        '''

    def _get_rates_for_base(self, base_currency):
        '''
        returns conversion rates for the provided base
        '''
        currency_url = '{0}/{1}?base={2}'.format(self.api_base_url,
                                                 'latest',
                                                 base_currency)
        fixer_response = requests.get(currency_url)
        if fixer_response.headers['content-type'] == 'text/html':
            raise exceptions.FixerError
        current_rates = fixer_response.json()['rates']
        return current_rates

if __name__ == '__main__':
    a = CurrencyConverter()
    for i in range(100):
        print(list(a.actual_rates['rates'].keys()), a.available_currencies)
