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
        self.symbols_map = self.get_symbols_map()

    def convert(self,
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

    def _get_actual_rates(self):
        '''
        Retrieves the actual currency conversion rates from fixer.io
        '''
