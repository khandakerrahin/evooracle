import csv
import math
import shutil
import sys
from config import *
import os
import json
import psutil
import re
import tiktoken
import datetime

from string_tables import string_tables

enc = tiktoken.get_encoding("cl100k_base")
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


def get_messages_tokens(messages):
    """
    Get the tokens of messages.
    :param messages: The messages.
    :return: The tokens.
    """
    cnt = 0
    for message in messages:
        cnt += count_tokens(message)
    return cnt


def count_tokens(strings):
    tokens = encoding.encode(strings)
    cnt = len(tokens)
    return cnt


def find_processes_created_by(pid):
    """
    Find the process's and all subprocesses' pid
    """
    parent_process = psutil.Process(pid)
    child_processes = parent_process.children(recursive=True)
    pids = [process.pid for process in child_processes]
    return pids.append(pid)


def remove_imports(code):
    # Define the regular expression pattern
    pattern = r"^import.*;$\n"

    # Use re.sub to remove lines matching the pattern
    output_str = re.sub(pattern, "", code, flags=re.MULTILINE)

    return output_str


def get_latest_file(file_dir, rounds=None, suffix=None):
    """
    Get the latest file
    :param file_dir:
    :return:
    """
    all_files = os.listdir(file_dir)
    file_number = len([x for x in all_files if x.endswith(".json")])
    if not suffix:
        for file in all_files:
            if file.startswith(str(file_number) + "_"):
                return os.path.join(file_dir, file)
    else:
        if not rounds:
            rounds = math.floor(file_number / 3)
        for file in all_files:
            if file.endswith(suffix + "_" + str(rounds) + ".json"):
                return os.path.join(file_dir, file)
    return ""


def get_dataset_path(method_id, project_name, class_name, method_name, direction):
    """
    Get the dataset path
    :return:
    """
    if direction == "raw":
        return os.path.join(dataset_dir, "raw_data",
                            method_id + "%" + project_name + "%" + class_name + "%" + method_name + "%raw.json")
    return os.path.join(dataset_dir, "direction_" + str(direction),
                        method_id + "%" + project_name + "%" + class_name + "%" + method_name + "%d" + str(
                            direction) + ".json")


def get_project_class_info(method_id, project_name, class_name, method_name):
    file_name = get_dataset_path(method_id, project_name, class_name, method_name, "raw")
    if os.path.exists(file_name):
        with open(file_name, "w") as f:
            raw_data = json.load(f)
        return raw_data["package"], raw_data["imports"]
    return None, None


def parse_file_name(filename):
    m_id, project_name, class_name, method_name, direction_and_test_num = filename.split('%')
    direction, test_num = direction_and_test_num.split('_')
    return m_id, project_name, class_name, method_name, direction, test_num.split('.')[0]


def parse_file_name(directory):
    dir_name = os.path.basename(directory)
    m_id, project_name, class_name, method_name, invalid = dir_name.split('%')
    return m_id, project_name, class_name, method_name


def get_raw_data(method_id, project_name, class_name, method_name):
    with open(get_dataset_path(method_id, project_name, class_name, method_name, "raw"), "r") as f:
        raw_data = json.load(f)
    return raw_data


# def get_project_abspath():
#     return os.path.abspath(project_dir)


def remove_single_test_output_dirs(project_path):
    prefix = "test_"

    # Get a list of all directories in the current directory with the prefix
    directories = [d for d in os.listdir(project_path) if os.path.isdir(d) and d.startswith(prefix)]

    # Iterate through the directories and delete them if they are not empty
    for d in directories:
        try:
            shutil.rmtree(d)
            print(f"Directory {d} deleted successfully.")
        except Exception as e:
            print(f"Error deleting directory {d}: {e}")


def get_date_string(directory_name):
    return directory_name.split('%')[1]


def find_result_in_projects():
    """
    Find the new directory.
    :return: The new directory.
    """
    all_results = [x for x in os.listdir(project_dir) if '%' in x]
    all_results = sorted(all_results, key=get_date_string)
    return os.path.join(result_dir, all_results[-1])


def find_newest_result():
    """
    Find the newest directory.
    :return: The new directory.
    """
    all_results = os.listdir(result_dir)
    all_results = sorted(all_results, key=get_date_string)
    return os.path.join(result_dir, all_results[-1])


def get_finished_project():
    projects = []
    all_directory = os.listdir(result_dir)
    for directory in all_directory:
        if directory.startswith("scope_test"):
            sub_dir = os.path.join(result_dir, directory)
            child_dir = ""
            for dir in os.listdir(sub_dir):
                if os.path.isdir(os.path.join(sub_dir, dir)):
                    child_dir = dir
                    break
            m_id, project_name, class_name, method_name = parse_file_name(child_dir)
            if project_name not in projects:
                projects.append(project_name)
    return projects


def get_openai_content(content):
    """
    Get the content for OpenAI
    :param content:
    :return:
    """
    if not isinstance(content, dict):
        return ""
    return content["choices"][0]['message']["content"]


def get_openai_message(content):
    """
    Get the content for OpenAI
    :param content:
    :return:
    """
    if not isinstance(content, dict):
        return ""
    return content["choices"][0]['message']


def check_java_version():
    # java_home = os.environ.get('JAVA_HOME')
    # if 'jdk-17' in java_home:
    #     return 17
    # elif 'jdk-11' in java_home:
    #     return 11
    # else:
    return 11

def repair_package(code, package_info):
    """
    Repair package declaration in test.
    """
    first_line = code.split('import')[0]
    if package_info == '' or package_info in first_line:
        return code
    code = package_info + "\n" + code
    return code


# TODO: imports can be optimized
def repair_imports(code, imports):
    """
    Repair imports in test.
    """
    import_list = imports.split('\n')
    first_line, _code = code.split('\n', 1)
    for _import in reversed(import_list):
        if _import not in code:
            _code = _import + "\n" + _code
    return first_line + '\n' + _code


def add_timeout(test_case, timeout=8000):
    """
    Add timeout to test cases. Only for Junit 5
    """
    # check junit version
    junit4 = 'import org.junit.Test'
    junit5 = 'import org.junit.jupiter.api.Test'
    if junit4 in test_case:  # Junit 4
        test_case = test_case.replace('@Test(', f'@Test(timeout = {timeout}, ')
        return test_case.replace('@Test\n', f'@Test(timeout = {timeout})\n')
    elif junit5 in test_case:  # Junit 5
        timeout_import = 'import org.junit.jupiter.api.Timeout;'
        test_case = repair_imports(test_case, timeout_import)
        return test_case.replace('@Test\n', f'@Test\n    @Timeout({timeout})\n')
    else:
        print("Can not know which junit version!")
        return test_case


def export_method_test_case(output, class_name, method_test_case):
    """
    Export test case to file.
    output : pathto/project/testcase.java
    """
    # method_test_case = add_timeout(method_test_case)
    # f = os.path.join(output, class_name + "_" + str(m_id) + '_' + str(test_num) + "Test.java")

    f = os.path.join(output, class_name + ".java")
    if not os.path.exists(output):
        os.makedirs(output)
    with open(f, "w") as output_file:
        output_file.write(method_test_case)
        return f


def change_class_name(test_case, old_name, new_name):
    """
    Change the class name in the test_case by given m_id.
    """
    return test_case.replace(old_name, new_name, 1)


def get_current_time():
    """
    Get current time
    :return:
    """
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")
    return formatted_time

def remove_all_assertions_but_last(source_code):
    # Regular expression pattern to match assertions
    assertion_pattern = r'(\w+\.)?(assert|assertTrue|assertNull|fail|assertFalse|assertNotEquals|assertEquals|assertArrayEquals|assertNotNull|assertNotSame|assertSame|assertThat)\s*\(.+?\);'

    # Find all matches of the assertion pattern in the source_code
    assertions = re.findall(assertion_pattern, source_code)

    # If there are no assertions, return the source_code as is
    if not assertions:
        return source_code

    # Initialize the replaced_assertions list
    replaced_assertions = []

    # Remove all but the last assertion
    for i in range(len(assertions) - 1):
        source_code = re.sub(assertion_pattern, "", source_code, count=1)
        # replaced_assertions.append(assertions[i][0] + assertions[i][1] + "()")

    return source_code

def get_CUT_from_test_class_name(input_string):
    parts = input_string.split(string_tables.EVOSUITE_SIGNATURE)
    if len(parts) > 0:
        return parts[0]
    else:
        parts = input_string.split(string_tables.TEST_SIGNATURE)

        if len(parts) > 0:
            return parts[0]
        else:
            return input_string  # Return the original string if "_ESTest" or "Test" is not found

def get_MUT_from_string(input_string):
    parts = input_string.split(".")
    if len(parts) >= 2:
        return parts[1]
    else:
        return input_string  # Return the original string if there's no second part or it can't be split

def remove_key_value_pair_from_json(data, key):
    # Iterate through the list of dictionaries and remove key-value pairs
    for item in data:
        # Remove the 'dependencies' key if it exists in the current dictionary
        if key in item:
            del item[key]

    # Convert the modified data back to JSON (if needed)
    json_data = json.dumps(data)
    return json_data

def write_entries_with_comments(context):
    # context = {"project_name", "class_name", "test_class_path", "test_class_name", 
    #        "test_method_name", "method_details", "test_method_code", "assertion_placeholder", "test_case_with_placeholder", "package", "evosuite_test_case"}
    
    data = context.get("method_details")
        
    comment_entries_file = "/home/shaker/evooracle_comments_entries.csv"
    # open file to write results
    if not os.path.exists(comment_entries_file):
        # If it doesn't exist, create the file with a header row
        with open(comment_entries_file, mode='w', newline='') as csv_file:
            
            fieldnames = ["project_name", "test_class_name", "test_method_name", "test_class_path", "dev_comments"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            
    # Iterate through the list of dictionaries and remove key-value pairs
    for item in data:
        # Remove the 'dependencies' key if it exists in the current dictionary
        if "dev_comments" in item:
            if item["dev_comments"]:
                with open(comment_entries_file, mode='a', newline='') as csv_file:
                    fieldnames = ["project_name", "test_class_name", "test_method_name", "test_class_path", "dev_comments"]
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    
                    writer.writerow({
                        "project_name": context.get("project_name"), 
                        "test_class_name": context.get("test_class_name"),  
                        "test_method_name": context.get("test_method_name"), 
                        "test_class_path": context.get("test_class_path"),  
                        "dev_comments": item["dev_comments"],
                    })
                break
    

def remove_empty_lines(input_text):
    lines = input_text.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    result = '\n'.join(non_empty_lines)
    return result

def replace_assertions(source_code):
    # Regular expression pattern to match assertions
    # Define the assertions to be replaced
    assertion_patterns = [
        r'(\w+\.)?assert\s*\(.+?\);',           # Matches ClassName.assert(...)
        r'(\w+\.)?assertTrue\s*\(.+?\);',       # Matches ClassName.assertTrue(...)
        r'(\w+\.)?assertNull\s*\(.+?\);',       # Matches ClassName.assertNull(...)
        r'(\w+\.)?fail\s*\(.+?\);',             # Matches ClassName.fail(...)
        r'(\w+\.)?assertFalse\s*\(.+?\);',      # Matches ClassName.assertFalse(...)
        r'(\w+\.)?assertNotEquals\s*\(.+?\);',  # Matches ClassName.assertNotEquals(...)
        r'(\w+\.)?assertEquals\s*\(.+?\);',     # Matches ClassName.assertEquals(...)
        r'(\w+\.)?assertArrayEquals\s*\(.+?\);',# Matches ClassName.assertArrayEquals(...)
        r'(\w+\.)?assertNotNull\s*\(.+?\);',    # Matches ClassName.assertNotNull(...)
        r'(\w+\.)?assertNotSame\s*\(.+?\);',    # Matches ClassName.assertNotSame(...)
        r'(\w+\.)?assertSame\s*\(.+?\);',       # Matches ClassName.assertSame(...)
        r'(\w+\.)?assertThat\s*\(.+?\);',       # Matches ClassName.assertThat(...)
    ]

    # List to store replaced assertions for this method
    replaced_assertions = []

    # Replace assertions with the placeholder
    for pattern in assertion_patterns:
        def replacement(match):
            # Get the matched text
            matched_text = match.group(0)
            # print(f"Pattern: {pattern}")
            # print(f"Replaced: {matched_text}")
            replaced_assertions.append(matched_text)
            return (string_tables.ASSERTION_PLACEHOLDER)

        source_code = re.sub(pattern, replacement, source_code)

    return source_code, replaced_assertions

def extract_assertions_from_string(input_string):
    # Regular expression pattern to match assertions
    assertion_patterns = [
        r'(\w+\.)?assert\s*\(.+?\);',           # Matches ClassName.assert(...)
        r'(\w+\.)?assertTrue\s*\(.+?\);',       # Matches ClassName.assertTrue(...)
        r'(\w+\.)?assertNull\s*\(.+?\);',       # Matches ClassName.assertNull(...)
        r'(\w+\.)?fail\s*\(.+?\);',             # Matches ClassName.fail(...)
        r'(\w+\.)?assertFalse\s*\(.+?\);',      # Matches ClassName.assertFalse(...)
        r'(\w+\.)?assertNotEquals\s*\(.+?\);',  # Matches ClassName.assertNotEquals(...)
        r'(\w+\.)?assertEquals\s*\(.+?\);',     # Matches ClassName.assertEquals(...)
        r'(\w+\.)?assertArrayEquals\s*\(.+?\);',# Matches ClassName.assertArrayEquals(...)
        r'(\w+\.)?assertNotNull\s*\(.+?\);',    # Matches ClassName.assertNotNull(...)
        r'(\w+\.)?assertNotSame\s*\(.+?\);',    # Matches ClassName.assertNotSame(...)
        r'(\w+\.)?assertSame\s*\(.+?\);',       # Matches ClassName.assertSame(...)
        r'(\w+\.)?assertThat\s*\(.+?\);',       # Matches ClassName.assertThat(...)
    ]

    # List to store extracted assertions
    extracted_assertions = []

    # Iterate through each pattern and find matches in the input string
    for pattern in assertion_patterns:
        matches = re.finditer(pattern, input_string)
        for match in matches:
            extracted_assertions.append(match.group(0))

    extracted_assertions = '\n'.join(extracted_assertions)
    return extracted_assertions

def extract_first_assertion_from_string(input_string):
    # Regular expression pattern to match assertions
    assertion_patterns = [
        r'(\w+\.)?assert\s*\(.+?\);',           # Matches ClassName.assert(...)
        r'(\w+\.)?assertTrue\s*\(.+?\);',       # Matches ClassName.assertTrue(...)
        r'(\w+\.)?assertNull\s*\(.+?\);',       # Matches ClassName.assertNull(...)
        r'(\w+\.)?fail\s*\(.+?\);',             # Matches ClassName.fail(...)
        r'(\w+\.)?assertFalse\s*\(.+?\);',      # Matches ClassName.assertFalse(...)
        r'(\w+\.)?assertNotEquals\s*\(.+?\);',  # Matches ClassName.assertNotEquals(...)
        r'(\w+\.)?assertEquals\s*\(.+?\);',     # Matches ClassName.assertEquals(...)
        r'(\w+\.)?assertArrayEquals\s*\(.+?\);',# Matches ClassName.assertArrayEquals(...)
        r'(\w+\.)?assertNotNull\s*\(.+?\);',    # Matches ClassName.assertNotNull(...)
        r'(\w+\.)?assertNotSame\s*\(.+?\);',    # Matches ClassName.assertNotSame(...)
        r'(\w+\.)?assertSame\s*\(.+?\);',       # Matches ClassName.assertSame(...)
        r'(\w+\.)?assertThat\s*\(.+?\);',       # Matches ClassName.assertThat(...)
    ]

    # Iterate through each pattern and find matches in the input string
    for pattern in assertion_patterns:
        match = re.search(pattern, input_string)
        if match:
            return match.group(0)

    
    return ""