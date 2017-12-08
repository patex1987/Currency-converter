'''
Created on 27. 11. 2017

@author: patex1987

This module contains code for the CurrencyConverter class
- CurrencyConverter can be used to convert amounts of money between different
currencies
- Actual conversion rates are downloaded from fixer.io website
- After downloading the actual rates, they are stored in a pickle file
- This pickle can be used to convert amounts in offline (of course the
actuality is questionable in offline mode)

Google style documentation is used in this file. See guideline here:
http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
'''

from collections import defaultdict
import datetime as dt
import io
import decimal
import json
import numbers
import os
import pickle
import requests
from requests.exceptions import ConnectionError
import currency_exceptions as exceptions
import pytz


class CurrencyConverter(object):
    '''This class handles all the currency conversion related operations

    Attributes:
        available_currencies(:obj:`list` of :obj:`str`): List of currently
            available currencies from fixer.io
        actual_rates (dict): Dictionary of conversion rates
    '''

    def __init__(self,
                 symbols_file=r'txt/symbols.txt',
                 symbols_sep='\t',
                 rates_file='rates.pickle'):
        '''CurrencyConverter's __init__ method

        Args:
            symbols_file (str): Description of `param1`.
            symbols_sep (str): Description of `param2`. Multiple
                lines are supported.
            rates_file (str): Description of `param3`.
        '''
        self._api_base_url = 'https://api.fixer.io'
        self._base_currency = 'EUR'
        self.available_currencies = []
        self._symbols_map = {}
        self._rates_file = rates_file
        try:
            self.actual_rates = self._check_rates_file(self._rates_file)
            self.available_currencies = self._get_available_currencies()
        except ConnectionError:
            return
        if symbols_file is not None:
            self._symbols_map = self._get_symbols_map(symbols_file, symbols_sep)

    def convert(self,
                input_amount,
                raw_input_currency,
                raw_output_currency=None):
        '''Method for currency conversion
        Converts the input amount into output currency. The result is a
        dictionary.

        Args:
            input_amount (:obj: `number.Number`): Amount to convert - any
                number type can be used, but try to use mainly floats or
                integers
            raw_input_currency (str): The input currency. Either a 3-letter
                currency code or a currency symbol
            raw_output_currency(:obj: `str`, optional): The output currency.
                Defaults to None. In case of None, the amount is converted to
                every available currency (self.available_currencies)

        Returns:
            dict: dictionary represenstation of the response

                {
                    "input": {
                        "amount": amount to be converted
                        "currency": input currency
                    },
                    "output": {
                        currency_code: output_amount
                    }
                }

            Note: if a conversion results in an error, the output node of the
            dictionary will contain the error message. Possible errors:
            1. ConnectionError - the conversion rates can't be downloaded,
            2. Unknown currency - a not known currency is provided
            3. Amount is not a number
            4. The input currency symbol represent more than one currency

            Other than that if you provide a symbol representing more than one
            currency as output currency, than the amount is converted to all
            currencies represented by that symbol. (E.g. $ can represent USD,
            AUD, NZD, etc.)

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
        '''Dumps the output of `convert` into json

        Args:
            conversion_dict (dict): output of the `convert` method. A
                dictionary representing the conversion results

        Returns:
            str: 3-letter currency code
        '''
        pretty_output = json.dumps(conversion_dict, indent=4, sort_keys=True)
        return pretty_output

    def _check_input_currency(self, raw_input_currency):
        '''Checks whether the input currency is in correct format

        Checks whether the `raw_input_currency` is a symbol or 3-letter code.
        At the end returns 3-letter currency code.

        Args:
            raw_input_currency (str): string representing the input currency to
                be checked by this method

        Returns:
            str: 3-letter currency code

        ConnectionError: If the currency conversion data from fixer.io can't be
            retrieved (`self.available_currencies` list is empty)
        exceptions.TooManyCurrencies: If the symbol represents more than one
            currency
        exceptions.CurrencyError: If an unknown currency is provided
        '''
        if not self.available_currencies:
            raise ConnectionError
        real_input_currency = raw_input_currency
        b_input_currency = bytes(raw_input_currency, encoding='utf-8')
        if b_input_currency in self._symbols_map.keys():
            input_currencies = self._symbols_map[b_input_currency]
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
        if b_output_currency in self._symbols_map.keys():
            possible_currencies = self._symbols_map[b_output_currency]
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

    def _convert_single_currency(self,
                                 input_amount,
                                 input_currency,
                                 output_currency):
        '''Converts `input_amount` into the `output_currency`

        '''
        actual_conversion_rate = self._calculate_current_rate(input_currency,
                                                              output_currency)
        output_amount = self._calculate_output_amount(input_amount,
                                                      actual_conversion_rate)
        return output_amount

    def _check_rates_file(self, file_path):
        '''
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
        act_currency = self._base_currency
        try:
            act_rates = self._get_rates_for_base(act_currency)
            act_rates[self._base_currency] = 1.0
            actual_rates['rates'][act_currency] = act_rates
            act_timestamp = dt.datetime.now(tz=pytz.timezone('CET'))
            actual_rates['last_update'] = act_timestamp
            if not os.path.isfile(self._rates_file):
                with open(self._rates_file, 'wb') as handle:
                    pickle.dump(actual_rates,
                                handle,
                                protocol=pickle.HIGHEST_PROTOCOL)
            return actual_rates
        except exceptions.FixerError:
            pass
        if not hasattr(self, 'actual_rates'):
            return actual_rates
        if actual_rates['last_update'] is None:
            return self.actual_rates

    def _get_available_currencies(self):
        '''
        gets a list of available currencies based on the actual_rates
        dictionary
        '''
        if not self.actual_rates:
            return []
        return list(self.actual_rates['rates'][self._base_currency].keys())

    def _get_symbols_map(self, file_name, separator):
        '''
        gets currency symbols mapping
        '''
        if not os.path.isfile(file_name):
            return {}
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
        '''
        last_update = self.actual_rates['last_update']
        next_update = last_update.replace(hour=16, minute=10)
        if last_update > next_update:
            next_update += dt.timedelta(days=1)
        if timestamp > next_update:
            self.actual_rates = self._get_actual_rates()
            with open(self._rates_file, 'wb') as handle:
                pickle.dump(self.actual_rates,
                            handle,
                            protocol=pickle.HIGHEST_PROTOCOL)
            self.available_currencies = self._get_available_currencies()

    def _calculate_current_rate(self, input_currency, output_currency):
        '''
        calculates the currency conversion rate needed to convert from input to
        output conversion. EUR is the basis currency
        '''
        if input_currency == output_currency:
            return 1.0
        if input_currency == self._base_currency:
            base_currency = self._base_currency
            return self.actual_rates['rates'][base_currency][output_currency]
        act_rates = self.actual_rates['rates'][self._base_currency]
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
        currency_url = '{0}/{1}?base={2}'.format(self._api_base_url,
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
