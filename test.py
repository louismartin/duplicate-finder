from collections import Counter
import os
import shutil

from find_duplicates import find_duplicates

enclosing_folder = os.path.dirname(os.path.realpath(__file__))
TEST_FOLDER = os.path.join(enclosing_folder, 'test_files')


def write_test_file(path, content):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, 'w') as f:
        f.write(content)


def assert_equal_lists_of_lists(lists1, lists2):
     def sort_list_of_lists(lists):
         lists = [sorted(l) for l in lists]
         return sorted(lists, key=lambda l: ''.join(l))

     assert sort_list_of_lists(lists1) == sort_list_of_lists(lists2)


def assert_duplicates_found(files_and_content, expected_duplicates):
    # Create test files
    for path, content in files_and_content:
        write_test_file(path, content)

    duplicate_lists = list(find_duplicates([TEST_FOLDER]))

    assert_equal_lists_of_lists(expected_duplicates, duplicate_lists)


def teardown_function():
    # Remove test files
    if os.path.exists(TEST_FOLDER):
            shutil.rmtree(TEST_FOLDER)


def test_find_duplicates():
    files_and_content = [
        (f'{TEST_FOLDER}/root1/1/1.txt', '1'),
        (f'{TEST_FOLDER}/root1/1/2.txt', '11'),

        (f'{TEST_FOLDER}/root2/1/1.txt', '1'),
        (f'{TEST_FOLDER}/root2/1/2.txt', '11'),
    ]
    expected_duplicates = [
        [f'{TEST_FOLDER}/root1', f'{TEST_FOLDER}/root2'],
    ]
    assert_duplicates_found(files_and_content, expected_duplicates)

    files_and_content = [
        (f'{TEST_FOLDER}/root1/1/1.txt', '1'),
        (f'{TEST_FOLDER}/root1/1/2.txt', '11'),
        (f'{TEST_FOLDER}/root1/2/1.txt', '111'),
        (f'{TEST_FOLDER}/root1/2/2.txt', '1111'),

        (f'{TEST_FOLDER}/root2/1/1.txt', '1'),
        (f'{TEST_FOLDER}/root2/1/2.txt', '11'),
        (f'{TEST_FOLDER}/root2/2/1.txt', '111'),
        (f'{TEST_FOLDER}/root2/2/2.txt', '999999999999999999999'),  # File's content differs
    ]
    expected_duplicates = [
        [f'{TEST_FOLDER}/root1/1', f'{TEST_FOLDER}/root2/1'],
        [f'{TEST_FOLDER}/root1/2/1.txt', f'{TEST_FOLDER}/root2/2/1.txt'],
    ]
    assert_duplicates_found(files_and_content, expected_duplicates)
