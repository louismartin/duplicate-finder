'''
Find files that are in paths_old but not in paths_new (orphans)
'''
import argparse
import time

from duplicate_finder.utils import explore_paths, size_to_str


def is_orphan(node, hashes_new):
    '''
    A node is an orphan if its hash is not in the new hashes and if all its
    childrens (recursively) have hashes that are not in the new hashes
    '''
    if node.is_leaf:
        return not node.hash_md5 in hashes_new

    return (not node.hash_md5 in hashes_new) and \
           all([is_orphan(child, hashes_new) for child in node.children])


def find_orphan_files(paths_old, paths_new):
    for path in paths_old:
        assert path not in paths_new

    print('Exploring paths')
    nodes_by_path_old = explore_paths(paths_old)
    nodes_by_path_new = explore_paths(paths_new)

    print('Computing hashes')
    hashes_new = set([node.hash_md5 for node in nodes_by_path_new.values()])

    print('Finding orphans')
    start = time.time()
    orphan_nodes = []
    for node in nodes_by_path_old.values():
        if is_orphan(node, hashes_new):
            orphan_nodes.append(node)
    print('\t{:.2f}s'.format(time.time() - start))

    # Keep only orphan nodes who don't have an orphan node as a parent
    print('Prune orphans')
    pruned_orphan_nodes = []
    for node in orphan_nodes:
        if not node.parent in orphan_nodes:
            pruned_orphan_nodes.append(node)
    orphan_nodes = pruned_orphan_nodes

    for node in sorted(orphan_nodes, key=lambda node: node.storage_path)[::-1]:
        print('{}\n\t{}'.format(size_to_str(node.storage_size), node.storage_path))
        yield node.storage_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--paths-old', required=True, nargs='+',
                        help=('Paths to look for orphans'))
    parser.add_argument('--paths-new', required=True, nargs='+',
                        help=('Paths to look for backups'))

    args = parser.parse_args()
    list(find_orphan_files(args.paths_old, args.paths_new))
