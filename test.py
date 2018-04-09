from collections import Counter
import os
import shutil

from find_duplicates import find_duplicates
from find_orphan_files import find_orphan_files

enclosing_folder = os.path.dirname(os.path.realpath(__file__))
TEST_FOLDER = os.path.join(enclosing_folder, 'test_files')


def write_test_file(path, n_bytes):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, 'wb') as f:
        f.write(b'\x00' * n_bytes)


def assert_equal_lists_of_lists(lists1, lists2):
     def sort_list_of_lists(lists):
         lists = [sorted(l) for l in lists]
         return sorted(lists, key=lambda l: ''.join(l))

     assert sort_list_of_lists(lists1) == sort_list_of_lists(lists2)


def assert_duplicates_found(files_and_content, expected_duplicates):
    # Create test files
    for path, n_bytes in files_and_content:
        write_test_file(path, n_bytes)

    duplicate_lists = list(find_duplicates([TEST_FOLDER]))

    assert_equal_lists_of_lists(expected_duplicates, duplicate_lists)


def teardown_function():
    # Remove test files
    if os.path.exists(TEST_FOLDER):
            shutil.rmtree(TEST_FOLDER)


def test_find_duplicates():
    files_and_content = [
        (f'{TEST_FOLDER}/root1/1/1.txt', 1),
        (f'{TEST_FOLDER}/root1/1/2.txt', 2),

        (f'{TEST_FOLDER}/root2/1/1.txt', 1),
        (f'{TEST_FOLDER}/root2/1/2.txt', 2),
    ]
    expected_duplicates = [
        [f'{TEST_FOLDER}/root1', f'{TEST_FOLDER}/root2'],
    ]
    assert_duplicates_found(files_and_content, expected_duplicates)

    files_and_content = [
        (f'{TEST_FOLDER}/root1/1/1.txt', 1),
        (f'{TEST_FOLDER}/root1/1/2.txt', 2),
        (f'{TEST_FOLDER}/root1/2/1.txt', 3),
        (f'{TEST_FOLDER}/root1/2/2.txt', 4),

        (f'{TEST_FOLDER}/root2/1/1.txt', 1),
        (f'{TEST_FOLDER}/root2/1/2.txt', 2),
        (f'{TEST_FOLDER}/root2/2/1.txt', 3),
        (f'{TEST_FOLDER}/root2/2/2.txt', 99),  # File's content differs
    ]
    expected_duplicates = [
        [f'{TEST_FOLDER}/root1/1', f'{TEST_FOLDER}/root2/1'],
        [f'{TEST_FOLDER}/root1/2/1.txt', f'{TEST_FOLDER}/root2/2/1.txt'],
    ]
    assert_duplicates_found(files_and_content, expected_duplicates)


def assert_orphans_found(paths_old, paths_new, files_and_content, expected_orphans):
    # Create test files
    for path, n_bytes in files_and_content:
        write_test_file(path, n_bytes)

    orphans = find_orphan_files(paths_old, paths_new)
    assert set(expected_orphans) == set(orphans)
    print(orphans)


def test_find_orphan_files():
    paths_old = [f'{TEST_FOLDER}/root1']
    paths_new = [f'{TEST_FOLDER}/root2']
    files_and_content = [
        (f'{TEST_FOLDER}/root1/1/1.txt', 1),
        (f'{TEST_FOLDER}/root1/1/2.txt', 2),
        (f'{TEST_FOLDER}/root1/2/1.txt', 3),
        # This file differs and is hence an orphan
        (f'{TEST_FOLDER}/root1/2/2.txt', 99),
        # This folder is an orphan
        (f'{TEST_FOLDER}/root1/3/1.txt', 5),
        (f'{TEST_FOLDER}/root1/3/2.txt', 6),
        # This file exists in another folder (not an orphan)
        (f'{TEST_FOLDER}/root1/5/1.txt', 9),

        (f'{TEST_FOLDER}/root2/1/1.txt', 1),
        (f'{TEST_FOLDER}/root2/1/2.txt', 2),
        (f'{TEST_FOLDER}/root2/2/1.txt', 3),
        (f'{TEST_FOLDER}/root2/2/2.txt', 4),
        (f'{TEST_FOLDER}/root2/4/1.txt', 7),
        (f'{TEST_FOLDER}/root2/4/2.txt', 8),
        (f'{TEST_FOLDER}/root2/6/1.txt', 9),
    ]
    expected_orphans = [
        f'{TEST_FOLDER}/root1/2/2.txt',
        f'{TEST_FOLDER}/root1/3',
    ]
    assert_orphans_found(paths_old, paths_new, files_and_content, expected_orphans)
