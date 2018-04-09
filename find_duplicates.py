import argparse
import time

import numpy as np

from duplicate_finder.utils import explore_paths, group_nodes_by_hash, size_to_str


def find_duplicates(root_paths):
    nodes_by_path = explore_paths(root_paths)

    # Regroup nodes by hash
    nodes_by_hash = group_nodes_by_hash(root_paths,
                                        nodes_by_path,
                                        skip_duplicates_children=True)
    duplicate_hashes = [k for k, v in nodes_by_hash.items() if len(v) > 1]

    # Compute duplicate sizes for each duplicate
    print('Getting duplicates sizes...')
    start = time.time()
    duplicated_sizes = []
    for hash_val in duplicate_hashes:
        duplicate_nodes = nodes_by_hash[hash_val]
        nb_duplicates = len(duplicate_nodes) - 1
        duplicated_size = nb_duplicates * duplicate_nodes[0].storage_size
        duplicated_sizes.append(duplicated_size)
    print('\t{:.2f}s'.format(time.time() - start))

    print('Sorting duplicates...')
    # Sort and print duplicated nodes by size
    for idx in np.argsort(duplicated_sizes)[::-1][:100]:
        nodes = nodes_by_hash[duplicate_hashes[idx]]
        print(size_to_str(duplicated_sizes[idx]))
        paths = [node.storage_path for node in nodes]
        print(''.join(['\t{}\n'.format(path) for path in paths]))
        yield paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', required=True, nargs='+',
                        help=('Paths from which to start the search for'
                              'duplicates'))

    args = parser.parse_args()
    list(find_duplicates(args.paths))
