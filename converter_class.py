'''
Created on 27. 11. 2017

@author: patex1987
'''

from collections import defaultdict
import datetime as dt
import io
import decimal
import json
import numbers
import requests
from requests.exceptions import ConnectionError
import currency_exceptions as exceptions
import pytz
import os
import pickle


class CurrencyConverter(object):
    '''
    This class handles all the currency conversion related operations
    '''

    def __init__(self, symbols_file=r'txt/symbols.txt', symbols_sep='\t'):
        '''
        Constructor
        '''
        self.api_base_url = 'https://api.fixer.io'
        self.base_currency = 'EUR'
        self.available_currencies = []
        self.symbols_map = {}
        try:
            self.actual_rates = self._get_actual_rates()
        except requests.exceptions.ConnectionError:
            return
        if symbols_file is not None:
            self.symbols_map = self._get_symbols_map(symbols_file, symbols_sep)

    def convert(self,
                input_amount,
                raw_input_currency,
                raw_output_currency=None):
        '''
        converts the input amount into a structured output
        output currency can be a single currency or all available currencies
        '''
        conversion_result = {}
        input_dict = self._get_input_dict(input_amount,
                                          raw_input_currency)
        conversion_result['input'] = input_dict
        conversion_result['output'] = {}
        try:
            input_currency = self._check_input_currency(raw_input_currency)
            output_currencies = self._check_output_currency(input_currency,
                                                            raw_output_currency)
            self._check_input_amount(input_amount)
            timestamp = dt.datetime.now(tz=pytz.timezone('CET'))
            self._check_rates_actuality(timestamp=timestamp)
            conversion_result['input'] = self._get_input_dict(input_amount,
                                                              input_currency)
            output_dict = self._get_all_conversions(input_amount,
                                                    input_currency,
                                                    output_currencies)
            conversion_result['output'] = output_dict
        except exceptions.ConversionError:
            err_str = 'Conversion error, check the input parameters'
            conversion_result['output']['error'] = err_str
        except exceptions.CurrencyError:
            err_str = 'Conversion error, the currency can\'t be' + \
                      ' recognized'
            conversion_result['output']['error'] = err_str
        except exceptions.TooManyCurrencies:
            err_str = 'Conversion error, the input symbol represents more ' + \
                      'than one currency, try to use 3-letter currency code'
            conversion_result['output']['error'] = err_str
        except ConnectionError:
            err_str = 'Connection error!'
            conversion_result['output']['error'] = err_str
        return conversion_result

    def stringify_output(self, conversion_dict):
        '''
        Returns conversion output in a pretty string format
        '''
        pretty_output = json.dumps(conversion_dict, indent=4, sort_keys=True)
        return pretty_output

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

    def _check_rates_file(self, file_path):
        '''
        TODO: improve this method, write tests
        checks, whether a pickle file with the rates exist. If yes loads the
        conversion rates from the pickle
        '''
        if not os.path.isfile(file_path):
            return self._get_actual_rates()
        with open(file_path, 'rb') as handle:
            actual_rates = pickle.load(handle)
        return actual_rates

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
            act_rates[self.base_currency] = 1.0
            actual_rates['rates'][act_currency] = act_rates
            actual_rates['last_update'] = dt.datetime.now(tz=pytz.timezone('CET'))
            self.available_currencies = list(act_rates.keys())
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
        with io.open(file_name, 'r', encoding='utf-8') as input_file:
            for line in input_file:
                data = line.strip().split(separator)
                if len(data) != 2:
                    raise exceptions.SymbolImportError
                symbol_encoded = bytes(data[0], encoding='utf-8')
                if len(data[1]) != 3:
                    raise exceptions.SymbolImportError
                if data[1] not in self.available_currencies:
                    continue
                currency = data[1]
                symbol_map[symbol_encoded].append(currency)
        return symbol_map

    def _get_all_conversions(self,
                             input_amount,
                             input_currency,
                             output_currencies):
        '''
        converts the input amount into all currencies in the output currencies
        list
        '''
        output_conversions = {}
        for currency in output_currencies:
            output_amount = self._convert_single_currency(input_amount,
                                                          input_currency,
                                                          currency)
            output_conversions[currency] = output_amount
        return output_conversions

    def _check_rates_actuality(self, timestamp):
        '''
        Check whether the actual_rates dictionary holds the newest currency
        rates
        TODO: pickle testing
        '''
        last_update = self.actual_rates['last_update']
        next_update = last_update.replace(hour=16, minute=10)
        if last_update > next_update:
            next_update += dt.timedelta(days=1)
        if timestamp > next_update:
            self.actual_rates = self._get_actual_rates()
            with open('rates.pickle', 'wb') as handle:
                pickle.dump(self.actual_rates,
                            handle,
                            protocol=pickle.HIGHEST_PROTOCOL)

    def _calculate_current_rate(self, input_currency, output_currency):
        '''
        calculates the currency conversion rate needed to convert from input to
        output conversion. EUR is the basis currency
        '''
        if input_currency == output_currency:
            return 1.0
        if input_currency == self.base_currency:
            base_currency = self.base_currency
            return self.actual_rates['rates'][base_currency][output_currency]
        act_rates = self.actual_rates['rates'][self.base_currency]
        input_val = decimal.Decimal(act_rates[input_currency])
        output_val = decimal.Decimal(act_rates[output_currency])

        rate = output_val / input_val
        precision = decimal.Decimal('.00001')
        rounding = decimal.ROUND_HALF_UP
        rounded_rate = decimal.Decimal(rate.quantize(precision,
                                                     rounding=rounding))

        return float(rounded_rate)

    def _calculate_output_amount(self, input_amount, conversion_rate):
        '''
        Returns the output amount
        '''
        dec_input = decimal.Decimal(input_amount)
        dec_conversion = decimal.Decimal(conversion_rate)
        output_amount = dec_input * dec_conversion
        precision = decimal.Decimal('.01')
        rounding = decimal.ROUND_HALF_UP
        rounded_output = decimal.Decimal(output_amount.quantize(precision,
                                                                rounding=rounding))
        return float(rounded_output)

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

    def _get_input_dict(self, amount, currency):
        '''
        converts amount and currency into a dictionary
        '''
        input_dict = {}
        input_dict['amount'] = amount
        input_dict['currency'] = currency
        return input_dict

    def _check_input_currency(self, raw_input_currency):
        '''
        Checks whether the input currency is in correct format and if its
        contained in the available currencies or symbols. Returns 3 letter
        currency codes (Converts symbol to currency)
        '''
        if not self.available_currencies:
            raise requests.exceptions.ConnectionError
        real_input_currency = raw_input_currency
        b_input_currency = bytes(raw_input_currency, encoding='utf-8')
        if b_input_currency in self.symbols_map.keys():
            input_currencies = self.symbols_map[b_input_currency]
            if len(input_currencies) != 1:
                raise exceptions.TooManyCurrencies
            real_input_currency = input_currencies[0]
        if real_input_currency in self.available_currencies:
            return real_input_currency
        raise exceptions.CurrencyError

    def _check_output_currency(self, real_input_currency, raw_output_currency):
        '''
        Checks whether the input currency is in correct format and if it
        exists. Returns a list of currency outputs
        '''
        if raw_output_currency is None:
            output_currencies = [currency for currency
                                 in self.available_currencies
                                 if currency != real_input_currency]
            return output_currencies
        b_output_currency = bytes(raw_output_currency, encoding='utf-8')
        if b_output_currency in self.symbols_map.keys():
            possible_currencies = self.symbols_map[b_output_currency]
            output_currencies = list(set(self.available_currencies) &
                                     set(possible_currencies) -
                                     set([real_input_currency]))
            return output_currencies
        if raw_output_currency in self.available_currencies:
            output_currencies = [raw_output_currency]
            return output_currencies
        raise exceptions.CurrencyError

    def _check_input_amount(self, input_amount):
        '''
        Checks whether the conversion parameters are in correct format
        '''
        if not isinstance(input_amount, numbers.Number):
            raise exceptions.ConversionError


if __name__ == '__main__':
    a = CurrencyConverter()
