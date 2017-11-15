import argparse

from duplicate_finder.duplicate_finder import find_duplicates


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+',
                        help=('Paths from which to start the search for'
                              'duplicates'))

    args = parser.parse_args()
    find_duplicates(args.paths)
