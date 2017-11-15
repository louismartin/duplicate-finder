from collections import defaultdict
import os
import time

import numpy as np
from tqdm import tqdm

from .hashnode import HashNode


def create_tree(root_path):
    root_node = HashNode(root_path[1:], is_file=False)
    # We need to save the nodes otherwise they will be lost outside the
    # method's scope.
    # TODO: Find another way to keep the nodes in memory
    nodes = {root_path: root_node}
    for (dirpath, dirnames, filenames) in tqdm(os.walk(root_path)):
        parent_node = nodes[dirpath]
        items = [(name, False) for name in dirnames] + \
                [(name, True) for name in filenames]
        for name, is_file in items:
            node = HashNode(name, parent=parent_node, is_file=is_file)
            path = os.path.join(dirpath, name)
            nodes[path] = node
    return root_node, nodes


def find_duplicates(paths):
    root_nodes = []
    all_nodes = []
    print('Discovering files...')
    for path in paths:
        # Create tree
        print('\t{}'.format(path))
        root_node, nodes = create_tree(path)
        root_nodes.append(root_node)
        all_nodes.extend(nodes)

    # Regroup nodes by hash
    print('Computing hashes and regrouping nodes...')
    start = time.time()
    nodes_by_hash = defaultdict(list)
    duplicate_hashes = set()
    nodes_to_explore = root_nodes[:]
    while len(nodes_to_explore) > 0:
        node = nodes_to_explore.pop()
        nodes_by_hash[node.hash_md5].append(node)
        if len(nodes_by_hash[node.hash_md5]) > 1:
            duplicate_hashes.add(node.hash_md5)
            # Don't explore the children for duplicate nodes (all children will
            # be nested smaller duplicates)
            continue
        nodes_to_explore.extend(node.children)
    print('\t{:.2f}s'.format(time.time() - start))

    # Compute total sizes of duplicates
    print('Getting duplicate sizes...')
    start = time.time()
    duplicate_hashes = list(duplicate_hashes)
    sizes = []
    for hash_val in duplicate_hashes:
        nodes = nodes_by_hash[hash_val]
        duplicated_size = (len(nodes) - 1) * nodes[0].storage_size
        sizes.append(duplicated_size)
    print('\t{:.2f}s'.format(time.time() - start))

    # Sort and print duplicated nodes by size
    print('Sorting duplicates...')
    start = time.time()
    for idx in np.argsort(sizes)[::-1][:10]:
        size = sizes[idx]
        nodes = nodes_by_hash[duplicate_hashes[idx]]
        print('{:0.2f} MB'.format(size/1e6))
        print(''.join(['\t{}\n'.format(node.storage_path) for node in nodes]))
    print('\t{:.2f}s'.format(time.time() - start))
