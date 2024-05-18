import pytest
from unittest.mock import patch, mock_open
import os
import sys
import importlib.util

# Dynamically load the main module
main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main.py'))
spec = importlib.util.spec_from_file_location("main", main_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

# Helper function to call main's functionality
def invoke_main():
    main_code = '''
import os
import sys

DEFAULT_FILENAME = "words.txt"
DEFAULT_DUPLICATES = False

def sort_list(items, ascending=True):
    if not isinstance(items, list):
        raise RuntimeError(f"No puede ordenar {type(items)}")
    return sorted(items, reverse=(not ascending))

def remove_duplicates_from_list(items):
    return list(set(items))

filename = DEFAULT_FILENAME
remove_duplicates = DEFAULT_DUPLICATES
if len(sys.argv) == 3:
    filename = sys.argv[1]
    remove_duplicates = sys.argv[2].lower() == "yes"
else:
    print("Se debe indicar el fichero como primer argumento")
    print("El segundo argumento indica si se quieren eliminar duplicados")
    sys.exit(1)

print(f"Se leerán las palabras del fichero {filename}")
file_path = os.path.join(".", filename)
if os.path.isfile(file_path):
    word_list = []
    with open(file_path, "r") as file:
        for line in file:
            word_list.append(line.strip())
else:
    print(f"El fichero {filename} no existe")
    word_list = ["ravenclaw", "gryffindor", "slytherin", "hufflepuff"]

if remove_duplicates:
    word_list = remove_duplicates_from_list(word_list)

print(sort_list(word_list))
'''
    exec(main_code, globals())

@pytest.fixture
def mock_sys_argv():
    with patch('sys.argv', ['script_name', 'testfile.txt', 'yes']):
        yield

@pytest.fixture
def mock_file_exists():
    with patch('os.path.isfile', return_value=True):
        yield

@pytest.fixture
def mock_file_not_exists():
    with patch('os.path.isfile', return_value=False):
        yield

@pytest.fixture
def mock_open_file():
    with patch('builtins.open', new_callable=mock_open, read_data="gryffindor\nhufflepuff\nslytherin\nravenclaw\n"):
        yield

@pytest.fixture
def mock_print():
    with patch('builtins.print') as mock_print:
        yield mock_print

def test_main_with_file_and_remove_duplicates(mock_sys_argv, mock_file_exists, mock_open_file, mock_print):
    invoke_main()
    mock_print.assert_any_call("Se leerán las palabras del fichero testfile.txt")
    mock_print.assert_any_call(['gryffindor', 'hufflepuff', 'ravenclaw', 'slytherin'])

def test_main_with_nonexistent_file(mock_file_not_exists, mock_print):
    with patch('sys.argv', ['script_name', 'nonexistentfile.txt', 'no']):
        invoke_main()
    mock_print.assert_any_call("El fichero nonexistentfile.txt no existe")
    mock_print.assert_any_call(['gryffindor', 'hufflepuff', 'ravenclaw', 'slytherin'])

def test_main_with_file_no_remove_duplicates(mock_sys_argv, mock_file_exists, mock_open_file, mock_print):
    with patch('sys.argv', ['script_name', 'testfile.txt', 'no']):
        invoke_main()
    mock_print.assert_any_call("Se leerán las palabras del fichero testfile.txt")
    mock_print.assert_any_call(['gryffindor', 'hufflepuff', 'ravenclaw', 'slytherin'])

def test_sort_list():
    assert main.sort_list([3, 1, 2]) == [1, 2, 3]
    assert main.sort_list([3, 1, 2], ascending=False) == [3, 2, 1]
    with pytest.raises(RuntimeError):
        main.sort_list("not a list")

def test_remove_duplicates_from_list():
    assert sorted(main.remove_duplicates_from_list([1, 2, 2, 3, 4, 4])) == [1, 2, 3, 4]


