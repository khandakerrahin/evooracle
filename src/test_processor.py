"""
This class will process all the test files: extract test cases, replace assertions, prepares contexts.
"""
import time
from resource_manager import ResourceManager
from string_tables import string_tables
from tools import *
from askLLM import start_whole_process, whole_process_with_LLM
from db_operations import database
from task import Task
from colorama import Fore, Style, init
import csv
import os
from datetime import datetime

init()
# db = database()

def create_temp_test_folder(project_dir):
    """
    Create a new folder for this scope test.
    :param direction: The direction of this scope test.
    :return: The path of the new folder.
    """
    # Get current time
    now = datetime.datetime.now()
    # format the time as a string
    time_str = now.strftime("%Y%m%d%H%M%S")
    result_path = os.path.join((project_dir+result_dir), "custom_test%" + time_str)
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

def prepare_test_cases_entries(project_dir):
    """
    - Iterates through tests
    - Prepares csv file with all entries
    :param project_dir:
    :return:    
    """
    if not os.path.exists(csv_entries_file):
        # If it doesn't exist, create the file with a header row
        with open(csv_entries_file, mode='w', newline='') as csv_file:
            fieldnames = ["ID"] + ["project_dir", "class_name", "method_name"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

    # Read the existing CSV file to find the last ID used
    last_id = 0
    with open(csv_entries_file, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            last_id = int(row["ID"])

    # Increment the last ID to generate a new ID
    new_id = last_id + 1

    with open(csv_entries_file, mode='a', newline='') as csv_file:
        fieldnames = ["ID"] + ["project_dir", "class_name", "method_name"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Write the header row
        # writer.writeheader()
    
        project_name = os.path.basename(os.path.normpath(project_dir))
        
        print("Project_name: ", Fore.GREEN + project_name, Style.RESET_ALL)
        
        # get the classes that contains tests.
        manager = ResourceManager(project_dir + db_file)
        class_results = manager.get_classes_with_contains_test(project_name)

        # Loop through the results
        for row in class_results:
            class_name = row.get("class_name")
            methods = row.get("methods")

            # Loop through the results
            for row in methods:
                project_name  = row.get("project_name")
                method_name = row.get("method_name")
                writer.writerow({
                    "ID": new_id,
                    "project_dir": project_dir,
                    "class_name": class_name,
                    "method_name": method_name
                })
                new_id = new_id + 1
            
        print("CSV generation: ", Fore.GREEN + "SUCCESS", Style.RESET_ALL)

def prepare_test_cases(test_id, project_dir, class_name, method_name, llm_name, consider_dev_comments):
    """
    - Get test details
    - Replaces Assertions
    - Prepares contexts for each tests
    :param project_dir:
    :param class_name:
    :param method_name:
    :return:    
    """
    
    project_name = os.path.basename(os.path.normpath(project_dir))
    
    print("Project Name: ", Fore.GREEN + project_name, Style.RESET_ALL)
    print("Test Class Name: ", Fore.GREEN + class_name, Style.RESET_ALL)
    print("Test Method Name: ", Fore.GREEN + method_name, Style.RESET_ALL)
    
    # delete the old result
    # remove_single_test_output_dirs(project_dir)

    # get the classes that contains tests.
    manager = ResourceManager(project_dir + db_file)
    class_details = manager.get_class_details_from_projectname_classname(project_name, class_name)

    signature = class_details.get("signature")
    super_class = class_details.get("super_class")
    package = class_details.get("package")
    stripped_package = class_details.get("package").split(' ')[1].strip(';')
    imports = class_details.get("imports")
    fields = class_details.get("fields")
    has_constructor = class_details.get("has_constructor")
    contains_test = class_details.get("contains_test")
    dependencies = class_details.get("dependencies")
    methods = class_details.get("methods")
    argument_list = class_details.get("argument_list")
    interfaces = class_details.get("interfaces")
    test_class_name = class_details.get("class_name")
    test_class_path = class_details.get("class_path")
    # print("class_name: ", class_name)
    # print("class_path: ", class_path)
    # print("signature: ", signature)
    # print("super_class: ", super_class)
    # print("package: ", package)
    # print("imports: ", imports)
    # print("fields: ", fields)
    # print("has_constructor: ", has_constructor)
    # print("contains_test: ", contains_test)
    # print("dependencies: ", dependencies)
    # print("methods: ", methods)
    # print("argument_list: ", argument_list)
    # print("interfaces: ", interfaces)
    
    # Define a list to store replaced assertions for each method
    replaced_assertions_per_method = {}

    test_method_details = manager.get_details_by_project_class_and_method(project_name, test_class_name, method_name, False)
    focal_methods = test_method_details["focal_methods"]
    source_code = test_method_details["source_code"]
    
    # project_name  = row.get("project_name")
    # method_signature = row.get("signature")
    # method_name = row.get("method_name")
    # focal_methods = row.get("focal_methods")
    # parameters = row.get("parameters")
    # source_code = row.get("source_code")
    # source_code_with_placeholder = row.get("source_code_with_placeholder")
    # class_name = row.get("class_name")
    # dependencies = row.get("dependencies")
    # use_field = row.get("use_field")
    # is_constructor = row.get("is_constructor")
    # is_test_method = row.get("is_test_method")
    # is_get_set = row.get("is_get_set")
    # is_public = row.get("is_public")
    # return_type = row.get("return_type")
    
    # print("project_name: ", project_name)
    # print("method_signature: ", method_signature)
    # print("method_name: ", method_name)
    # print("focal_method_name: ", focal_method_name)
    # print("parameters: ", parameters)
    # print("source_code: ", source_code)
    # print("source_code_with_placeholder: ", source_code_with_placeholder)
    # print("class_name: ", class_name)
    # print("dependencies: ", dependencies)
    # print("use_field: ", use_field)
    # print("is_constructor: ", is_constructor)
    # print("is_test_method: ", is_test_method)
    # print("is_get_set: ", is_get_set)
    # print("is_public: ", is_public)
    # print("return_type: ", return_type)


    # print("SOURCE CODE: " + source_code)

    source_code = remove_all_assertions_but_last(source_code)

    source_code = remove_empty_lines(source_code)

    # print("SIMPLIFIED SOURCE CODE: " + source_code)

    # prepare the test case
    evosuite_test_case = package + string_tables.NL +  imports + string_tables.NL + signature + string_tables.NL + string_tables.LEFT_CURLY_BRACE + string_tables.NL + source_code + string_tables.NL + string_tables.RIGHT_CURLY_BRACE

    # Regular expression pattern to match assertions
    source_code, replaced_assertions = replace_assertions(source_code)

    # print("UPDATED SOURCE CODE: " + source_code)
    # print("replaced_assertions: "+ '\n'.join(replaced_assertions))
    
    # prepare the test case
    test_case_with_placeholder = package + string_tables.NL +  imports + string_tables.NL + signature + string_tables.NL + string_tables.LEFT_CURLY_BRACE + string_tables.NL + source_code + string_tables.NL + string_tables.RIGHT_CURLY_BRACE

    test_method_details["source_code_with_placeholder"] = source_code

    # focal_methods = json.loads(focal_method_name)
    
    # overriding the CUT from DB Json to Test Filename
    class_under_test = get_CUT_from_test_class_name(test_class_name)

    # prepare the context
    MUT_list = set()  # Create an empty set to store unique MUT
    
    for focal_method in focal_methods:
        mut = get_MUT_from_string(focal_method)
        MUT_list.add(mut)

    MUT_list = list(MUT_list)
    
    method_details_list = []

    for MUT in MUT_list:
        method_details = manager.get_details_by_project_class_and_method(project_name, class_under_test, MUT, True)
        if method_details:
            method_details_list.append(method_details)
    
    # print("CUT: ", Fore.GREEN + class_under_test, Style.RESET_ALL)
    # print("MUT: \n", Fore.YELLOW + "\n".join(MUT_list), Style.RESET_ALL)
    # print()
    
    # method_under_test_details = manager.get_details_by_project_class_and_method(project_name, class_under_test, method_under_test, False)

    # # print(method_under_test_details)
    # if method_under_test_details:
    #     dev_comments = method_under_test_details.get("dev_comments")
    # else:
    #     dev_comments = None

    context = {"project_name": project_name, "class_name": class_under_test, "test_class_path":test_class_path, "test_class_name": test_class_name, 
           "test_method_name":method_name, "method_details": method_details_list, "test_method_code": source_code, 
            "assertion_placeholder": string_tables.ASSERTION_PLACEHOLDER, "test_case_with_placeholder":test_case_with_placeholder, 
            "package":stripped_package, "evosuite_test_case":evosuite_test_case}
    
    # Store replaced assertions for this method in the dictionary
    replaced_assertions_per_method[method_name] = replaced_assertions
    
    # open file to write results
    if not os.path.exists(final_result_file):
        # If it doesn't exist, create the file with a header row
        with open(final_result_file, mode='w', newline='') as csv_file:
            # test_id, time, attempts, assertion_generated, is_compiled, is_run, mutation_score, CUT, MUT, project_dir, eo_assertions, 
            fieldnames = ["test_id", "total_time", "assertion_generation_time", "attempts", "assertion_generated", "eo_is_compiled", "eo_is_run", 
                          "eo_mutation_score", "es_is_compiled", "es_is_run", "es_mutation_score", "CUT", "MUT", "project_dir", "eo_assertions", 
                          "used_developer_comments", "model", "temperature", "n_predict", "top_p", "top_k", "n_batch", "repeat_penalty", 
                          "repeat_last_n", "timestamp", "prompts_and_responses"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

    # Get the current time in milliseconds
    start_time = time.perf_counter()
    
    result = {
        "assertion_generation_time": None,
        "attempts": None, 
        "assertion_generated": None,
        "eo_is_compiled": None,
        "eo_is_run": None,
        "eo_mutation_score": None,
        "es_is_compiled": None,
        "es_is_run": None,
        "es_mutation_score": None,
        "eo_assertions": None,
        "prompts_and_responses": None,
    }
    result = whole_process_with_LLM(project_dir, context, test_id, llm_name, consider_dev_comments)
    
    end_time = time.perf_counter()

    total_time = (end_time - start_time) * 1000
    # Get the current timestamp as a string
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(final_result_file, mode='a', newline='') as csv_file:
        fieldnames = ["test_id", "total_time", "assertion_generation_time", "attempts", "assertion_generated", "eo_is_compiled", "eo_is_run", 
                          "eo_mutation_score", "es_is_compiled", "es_is_run", "es_mutation_score", "CUT", "MUT", "project_dir", "eo_assertions", 
                          "used_developer_comments", "model", "temperature", "n_predict", "top_p", "top_k", "n_batch", "repeat_penalty", 
                          "repeat_last_n", "timestamp", "prompts_and_responses"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writerow({
            "test_id": test_id, 
            "total_time": total_time,
            "assertion_generation_time": result["assertion_generation_time"],
            "attempts": result["attempts"], 
            "assertion_generated": result["assertion_generated"],
            "eo_is_compiled": result["eo_is_compiled"],
            "eo_is_run": result["eo_is_run"],
            "eo_mutation_score": result["eo_mutation_score"],
            "es_is_compiled": result["es_is_compiled"],
            "es_is_run": result["es_is_run"],
            "es_mutation_score": result["es_mutation_score"],
            "CUT": class_under_test,
            "MUT": method_details_list,
            "project_dir": project_dir,
            "eo_assertions": result["eo_assertions"],
            "model": llm_name,
            "temperature": temperature, 
            "n_predict": n_predict, 
            "top_p": top_p,
            "top_k": top_k,
            "n_batch": n_batch,
            "repeat_penalty": repeat_penalty,
            "repeat_last_n": repeat_last_n,
            "used_developer_comments": consider_dev_comments,
            "prompts_and_responses": result["prompts_and_responses"],
            "timestamp": current_time,
        })
 
        print("Result generation: ", Fore.GREEN + "SUCCESS", Style.RESET_ALL)

    print("WHOLE PROCESS FINISHED")

def start_generation(project_dir, sql_query, multiprocess=True, repair=True, confirmed=False):
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
    remove_single_test_output_dirs(project_dir)

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
