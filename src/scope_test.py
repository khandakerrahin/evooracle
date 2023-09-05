"""
This file is for starting a scope test for selected methods.
It will automatically create a new folder inside dataset as well as result folder.
The folder format is "scope_test_YYYYMMDDHHMMSS_Direction".
The dataset folder will contain all the information in the direction.
"""
import time
from string_tables import string_tables
from tools import *
from askLLM import start_whole_process
from db_operations import database
from task import Task
from colorama import Fore, Style, init

init()
db = database()

def create_temp_test_folder():
    """
    Create a new folder for this scope test.
    :param direction: The direction of this scope test.
    :return: The path of the new folder.
    """
    # Get current time
    now = datetime.datetime.now()
    # format the time as a string
    time_str = now.strftime("%Y%m%d%H%M%S")
    result_path = os.path.join(result_dir, "custom_test%" + time_str)
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    else:
        raise Exception("Result folder already exists.")
    return result_path

def create_dataset_result_folder(direction):
    """
    Create a new folder for this scope test.
    :param direction: The direction of this scope test.
    :return: The path of the new folder.
    """
    # Get current time
    now = datetime.datetime.now()
    # format the time as a string
    time_str = now.strftime("%Y%m%d%H%M%S")
    result_path = os.path.join(result_dir, "scope_test%" + time_str + "%" + direction)
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    else:
        raise Exception("Result folder already exists.")
    return result_path


def create_new_folder(folder_path: str):
    """
    Create a new folder.
    :param folder_path: The folder path.
    :return: None
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        raise Exception("Folder already exists.")


def find_all_files(folder_path: str, method_ids: list = None):
    """
    Find all the files in the folder.
    :param method_ids: The method ids need to be found.
    :param folder_path: The folder path.
    :return: The file list.
    """
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.split("%")[0] not in method_ids:
                continue
            file_list.append(file)
    return file_list

def prepare_test_cases(sql_query, multiprocess=True, repair=True, confirmed=False):
    """
    Start the scope test.
    :param multiprocess: if it needs to
    :param repair:
    :param sql_query:
    :return:    
    """
    match = re.search(r"project_name\s*=\s*'([\w-]*)'", sql_query)
    if match:
        project_name = match.group(1)
        print("Project_name: ", Fore.GREEN + project_name, Style.RESET_ALL)
    else:
        raise RuntimeError("One project at one time.")
    # delete the old result
    remove_single_test_output_dirs(get_project_abspath())

    # SQL query to get the classes that contains tests.
    # sql_query_class = """
    # SELECT id, class_name, class_path, signature, super_class, package, imports, fields, has_constructor, contains_test, dependencies 
    # FROM class where contains_test is true AND project_name='{}';
    # """.format(project_name)

    # Execute the SQL query and retrieve the results
    class_results = db.select(script=sql_query)

    # Loop through the results
    for row in class_results:
        id, class_name, class_path, class_signature, super_class, package, imports, fields, has_constructor, contains_test, dependencies = row
        
        # print("id: ", id)
        # print("class_name: ", class_name)
        # print("class_path: ", class_path)
        # print("signature: ", class_signature)
        # print("super_class: ", super_class)
        # print("package: ", package)
        # print("imports: ", imports)
        # print("fields: ", fields)
        # print("has_constructor: ", has_constructor)
        # print("contains_test: ", contains_test)
        # print("dependencies: ", dependencies)

        # SQL query to get the classes that contains tests.
        sql_query_methods = """
        SELECT id, project_name, signature, focal_method_name, method_name, parameters, 
        source_code, class_name, dependencies, use_field, is_constructor, is_test_method, is_get_set, is_public 
        FROM method where is_test_method is true AND project_name='{}' and class_name='{}';
        """.format(project_name, class_name)

        # Execute the SQL query and retrieve the results
        method_results = db.select(script=sql_query_methods)

        
        # Create the new folder
        result_path = create_temp_test_folder()

        if not method_results:
            raise Exception("Test Method ids cannot be None.")
        if not isinstance(method_results, str):
            method_ids = [str(i[0]) for i in method_results]
        print("You are about to start the whole process of scope test.")
        print("The number of tests is ", len(method_ids), ".")
        
        record = "This is a record of a scope test.\n"
        
        # if not confirmed:
        #     confirm = input("Are you sure to start the scope test? (y/n): ")
        #     if confirm != "y":
        #         print("Scope test cancelled.")
        #         return

        

        record += "Result path: " + result_path + "\n"
        record += 'SQL script: "' + sql_query + '"\n'
        record += "Included test methods: " + str(method_ids) + "\n"

        record_path = os.path.join(result_path, "record.txt")
        with open(record_path, "w") as f:
            f.write(record)
        print(Fore.GREEN + "The record has been saved at", record_path, Style.RESET_ALL)

        # Define a list to store replaced assertions for each method
        replaced_assertions_per_method = {}

        # Loop through the results
        for row in method_results:
            id, project_name, method_signature, focal_method_name, method_name, parameters, source_code, class_name, dependencies, use_field, is_constructor, is_test_method, is_get_set, is_public  = row
            # print("id: ", id)
            # print("project_name: ", project_name)
            # print("signature: ", method_signature)
            # print("focal_method_name: ", focal_method_name)
            # print("method_name: ", method_name)
            # print("parameters: ", parameters)
            # print("source_code: ", source_code)
            # print("class_name: ", class_name)
            # print("dependencies: ", dependencies)
            # print("use_field: ", use_field)
            # print("is_constructor: ", is_constructor)
            # print("is_test_method: ", is_test_method)
            # print("is_get_set: ", is_get_set)
            # print("is_public: ", is_public)
            
            # Regular expression pattern to match assertions
            # Define the assertions to be replaced
            assertion_patterns = [
                r'assert\s*\(.+?\);',
                r'assertTrue\s*\(.+?\);',
                r'assertNull\s*\(.+?\);',
                r'fail\s*\(.+?\);',
                r'assertFalse\s*\(.+?\);',
                r'assertNotEquals\s*\(.+?\);',
                r'assertEquals\s*\(.+?\);',
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
                    return (string_tables.NL + string_tables.ASSERTION_PLACEHOLDER)

                source_code = re.sub(pattern, replacement, source_code)
            test_case = package + string_tables.NL +  imports + string_tables.NL + class_signature + string_tables.NL + string_tables.LEFT_CURLY_BRACE + string_tables.NL + source_code + string_tables.NL + string_tables.RIGHT_CURLY_BRACE

            # update Method to add the sourcecode_with_placeholder
            db.update("method", conditions = {"id": id}, new_cols = {"source_code_with_placeholder": source_code})
                                         
            # Store replaced assertions for this method in the dictionary
            replaced_assertions_per_method[method_name] = replaced_assertions
            
            # print("..........................................................................")
            # time.sleep(0)
        
        # Print the modified Java test method
        # print(replaced_assertions_per_method)
            




    

    # Find all the files
    source_dir = os.path.join(dataset_dir, "direction_1")

    # start_whole_process(source_dir, result_path, multiprocess=multiprocess, repair=repair)
    print("WHOLE PROCESS FINISHED")
    # Run accumulated tests
    # project_path = os.path.abspath(project_dir)
    # print("START ALL TESTS")

    # Task.all_test(result_path, project_path)
    # try:
    #     with open(record_path, "a") as f:
    #         f.write("Whole test result at: " + find_result_in_projects() + "\n")
    # except Exception as e:
    #     print("Cannot save whole test result.")
    #     print(e)

    # print("SCOPE TEST FINISHED")

def start_generation(sql_query, multiprocess=True, repair=True, confirmed=False):
    """
    Start the scope test.
    :param multiprocess: if it needs to
    :param repair:
    :param sql_query:
    :return:    
    """
    match = re.search(r"project_name\s*=\s*'([\w-]*)'", sql_query)
    if match:
        project_name = match.group(1)
        print("Project_name: ", Fore.GREEN + project_name, Style.RESET_ALL)
    else:
        raise RuntimeError("One project at one time.")
    # delete the old result
    remove_single_test_output_dirs(get_project_abspath())

    method_ids = [x[0] for x in db.select(script=sql_query)]
    if not method_ids:
        raise Exception("Test Method ids cannot be None.")
    if not isinstance(method_ids[0], str):
        method_ids = [str(i) for i in method_ids]
    print("You are about to start the whole process of scope test.")
    print("The number of tests is ", len(method_ids), ".")
    # print("The approximate cost will be", Fore.RED + "$", len(method_ids) * 0.0184 * test_number, ".", Style.RESET_ALL)
    record = "This is a record of a scope test.\n"
    # if not confirmed:
    #     confirm = input("Are you sure to start the scope test? (y/n): ")
    #     if confirm != "y":
    #         print("Scope test cancelled.")
    #         return

    # Create the new folder
    result_path = create_dataset_result_folder("")

    record += "Result path: " + result_path + "\n"
    record += 'SQL script: "' + sql_query + '"\n'
    record += "Included test methods: " + str(method_ids) + "\n"

    record_path = os.path.join(result_path, "record.txt")
    with open(record_path, "w") as f:
        f.write(record)
    print(Fore.GREEN + "The record has been saved at", record_path, Style.RESET_ALL)

    # Find all the files
    source_dir = os.path.join(dataset_dir, "direction_1")

    start_whole_process(source_dir, result_path, multiprocess=multiprocess, repair=repair)
    print("WHOLE PROCESS FINISHED")
    # Run accumulated tests
    # project_path = os.path.abspath(project_dir)
    # print("START ALL TESTS")

    # Task.all_test(result_path, project_path)
    # try:
    #     with open(record_path, "a") as f:
    #         f.write("Whole test result at: " + find_result_in_projects() + "\n")
    # except Exception as e:
    #     print("Cannot save whole test result.")
    #     print(e)

    # print("SCOPE TEST FINISHED")


if __name__ == '__main__':
    sql_query = "SELECT id FROM method WHERE project_name='Lang_1_f' AND class_name='NumberUtils' AND is_constructor=0;"
    start_generation(sql_query, multiprocess=True, repair=True, confirmed=False)
