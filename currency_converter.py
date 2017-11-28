'''
Created on 27. 11. 2017

@author: patex1987
'''


class CurrencyConverter(object):
    '''
    This class handles all the currency conversion related operations
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.actual_rates = self._get_actual_rates()
        self.symbols_map = self._get_symbols_map()
        self.available_currencies = self._get_available_currencies()

    def convert(self,
                input_amount,
                input_currency,
                output_currency=None):
        '''
        converts the input amount into a structured output
        output curency can be a single currency or all available currencies
        '''
        output_currencies = self._get_current_outputs(input_currency,
                                                      output_currency)
        output_amounts = self._get_all_conversions(input_amount,
                                                   input_currency,
                                                   output_currencies)
        return output_amounts

    def convert_single_currency(self,
                                input_amount,
                                input_currency,
                                output_currency):
        '''
        Converts the provided input amount of money into the desired output
        amount
        '''
        self._check_rates_actuality()
        actual_conversion_rate = self._calculate_current_rate(input_currency,
                                                              output_currency)
        output_amount = self._calculate_output_amount(input_amount,
                                                      actual_conversion_rate)
        return output_amount

    def _get_actual_rates(self):
        '''
        Retrieves the actual currency conversion rates from fixer.io
        '''

    def _get_symbols_map(self):
        '''
        gets currency symbols mapping
        '''

    def _get_available_currencies(self):
        '''
        returns a list of available ouput currencies
        '''

    def _get_current_outputs(self, input_currency, output_currency):
        '''
        returns a list of possible output currencies for the selected input
        currency
        '''

    def _get_all_conversions(input_amount, input_currency, output_currencies)
        output_conversions = {}
        for currency in output_currencies:
            output_amount = self.convert_single_currency(input_amount,
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


