
import argparse
import logging
import os


def parse() -> os.path:
    """
    Perform parsing of command line arguments and execute the analysis.

    :return os.path: The path to the output SAM file with information about mapped reads.
    """
    parser = argparse.ArgumentParser(
        prog='Pridumat pozje',
        description='This project is an attempt to create a bwt aliner',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='Good luck!   (∿°○°)∿ .・。.・゜✭・.・。.・゜✭・.・。.・゜✭')

    
    parser.add_argument('-r', '--reads',
                        default=None, type=str, help='File with reads')
    parser.add_argument('-ref', '--reference_sequence',
                        default=None, type=str, help='Reference sequence to align to')
    parser.add_argument('-od', '--output_directory', type=str,
                        default=f'{os.getcwd()}', help='The path to the save directory')
    parser.add_argument('-lg', '--logging', type=bool, choices=(True, False),
                        default=False, help='Enables logging')
    parser.add_argument('-t', '--threads', type=int,
                        default=1, help='Parameter for specifying the number of threads')
    args = parser.parse_args()
    logger = logging.getLogger()
    logger.disabled = not args.logging

    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)




if __name__ == "__main__":
    parse()
