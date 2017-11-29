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
