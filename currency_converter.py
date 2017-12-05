'''
Created on 5. 12. 2017

Command line interface for the converter class
Can be used to convert money between different currencies

@author: patex1987
'''
import argparse
import sys


def main(arguments):
    print(len(arguments))


def get_parser():
    '''
    Gets the command line parser
    '''
    parser = argparse.ArgumentParser(description="Log File converter")
    parser.add_argument("-input_amount",
                        required=True,
                        type=float,
                        dest='raw_input_amount',
                        help="Input amount to be converted")
    parser.add_argument('-input_currency',
                        required=True,
                        dest='raw_input_currency',
                        help='Input currency. 2 options: 3-letter currency ' +
                             'code; currency symbol')
    parser.add_argument('-output_currency',
                        default=None,
                        dest='raw_output_currency',
                        help='Output currency. 2 options: 3-letter currency ' +
                             'code; currency_symbol. Optional paramter, if ' +
                             'omitted, all available currencies will be used')
    return parser


if __name__ == '__main__':
    ARGS = get_parser().parse_args()
    sys.exit(main(*ARGS))