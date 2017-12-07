'''
Created on 5. 12. 2017

Command line interface for the converter class
Can be used to convert money between different currencies

@author: patex1987
'''
import argparse
import sys
from converter_class import CurrencyConverter


def main(arguments):
    '''
    '''
    converter = CurrencyConverter()
    conv_result = converter.convert(arguments.raw_input_amount,
                                    arguments.raw_input_currency,
                                    arguments.raw_output_currency)
    output = converter.stringify_output(conv_result)
    print(output)


def get_parser():
    '''
    Gets the command line parser
    '''
    parser = argparse.ArgumentParser(description="Currency converter CLI")
    parser.add_argument("--amount",
                        required=True,
                        type=float,
                        dest='raw_input_amount',
                        help="Input amount to be converted")
    parser.add_argument('--input_currency',
                        required=True,
                        dest='raw_input_currency',
                        help='Input currency. 2 options: 3-letter currency ' +
                             'code; currency symbol')
    parser.add_argument('--output_currency',
                        default=None,
                        dest='raw_output_currency',
                        help='Output currency. 2 options: 3-letter currency ' +
                             'code; currency_symbol. Optional parameter, if ' +
                             'omitted, all available currencies will be used')
    return parser


if __name__ == '__main__':
    ARGS = get_parser().parse_args()
    sys.exit(main(ARGS))
