'''
Created on 28. 11. 2017

@author: patex1987
'''


class FixerError(Exception):
    '''
    Exception for handling connectivity errors with fixer.io
    '''
    pass


class SymbolImportError(Exception):
    '''
    Exception for handling errors, if improper separator is used for symbol
    map importing
    '''
    pass


class ConversionError(Exception):
    '''
    Exception, if conversion can't be done
    '''
    pass


class CurrencyError(Exception):
    '''
    Exception thrown, if a wrong currency is provided
    '''
    pass


class TooMuchCurrencies(Exception):
    '''
    Exception thrown, if too much currencies are mapped to the provided
    currency symbol
    '''
    pass