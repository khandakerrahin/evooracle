"""
This class will process all the test files: extract test cases, replace assertions, prepares contexts.
It will automatically create a new folder inside dataset as well as result folder.
The folder format is "scope_test_YYYYMMDDHHMMSS_Direction".
The dataset folder will contain all the information in the direction.
"""
import time
from resource_manager import ResourceManager
from string_tables import string_tables
from tools import *
from askLLM import start_whole_process, whole_process_with_LLM
from db_operations import database
from task import Task
from colorama import Fore, Style, init

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

def prepare_test_cases(project_dir):
    """
    - Iterates through tests
    - Replaces Assertions
    - Prepares contexts for each tests
    :param project_dir:
    :return:    
    """
    
    project_name = os.path.basename(os.path.normpath(project_dir))
    
    print("Project_name: ", Fore.GREEN + project_name, Style.RESET_ALL)
    
    # delete the old result
    remove_single_test_output_dirs(project_dir)

    # get the classes that contains tests.
    manager = ResourceManager(project_dir + db_file)
    class_results = manager.get_classes_with_contains_test(project_name)

    # Loop through the results
    for row in class_results:
        class_name = row.get("class_name")
        class_path = row.get("class_path")
        signature = row.get("signature")
        super_class = row.get("super_class")
        package = row.get("package")
        imports = row.get("imports")
        fields = row.get("fields")
        has_constructor = row.get("has_constructor")
        contains_test = row.get("contains_test")
        dependencies = row.get("dependencies")
        methods = row.get("methods")
        argument_list = row.get("argument_list")
        interfaces = row.get("interfaces")
        
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
        
        
        # Create the new folder
        result_path = create_temp_test_folder(project_dir)

        print("All the classes and tests are loaded.")
        
        print("The number of tests is ", len(methods), ".")
        
        record = "This is a record of a scope test.\n"
        
        # if not confirmed:
        #     confirm = input("Are you sure to start the scope test? (y/n): ")
        #     if confirm != "y":
        #         print("Scope test cancelled.")
        #         return

        

        record += "Result path: " + result_path + "\n"
        method_names = [obj.get("method_name") for obj in methods]
        record += "Included test methods: " + ", ".join(method_names) + "\n"
        record_path = os.path.join(result_path, "record.txt")

        with open(record_path, "w") as f:
            f.write(record)
        print(Fore.GREEN + "The record has been saved at", record_path, Style.RESET_ALL)


        submits = 0
        total = len(methods) * test_number
        
        # Define a list to store replaced assertions for each method
        replaced_assertions_per_method = {}

        # Loop through the results
        for row in methods:
            project_name  = row.get("project_name")
            method_name = row.get("method_name")
            focal_methods = row.get("focal_methods")
            source_code = row.get("source_code")

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

            # Regular expression pattern to match assertions
            source_code, replaced_assertions = replace_assertions(source_code)


            # prepare the test case
            test_case = package + string_tables.NL +  imports + string_tables.NL + signature + string_tables.NL + string_tables.LEFT_CURLY_BRACE + string_tables.NL + source_code + string_tables.NL + string_tables.RIGHT_CURLY_BRACE

            row["source_code_with_placeholder"] = source_code

            # focal_methods = json.loads(focal_method_name)
            
            # prepare the context
            class_under_test, method_under_test = (focal_methods[0]).split(".")
            
            # print("CUT: ", class_under_test)
            # print("MUT: ", method_under_test)
            # print()

            manager.get_details_by_project_class_and_method
            
            context = {"project_name": project_name, "class_name": class_under_test, "method_name": method_under_test, 
                       "method_details": manager.get_details_by_project_class_and_method(project_name, class_under_test, method_under_test, True), 
                       "test_method_code": source_code, "assertion_placeholder": string_tables.ASSERTION_PLACEHOLDER, "test_case":test_case, "package":package}
            
            # Store replaced assertions for this method in the dictionary
            replaced_assertions_per_method[method_name] = replaced_assertions
            
            # print("..........................................................................")
            # time.sleep(0)

            for test_num in range(1, test_number + 1):
                submits += 1
                # whole_process(test_num, base_name, base_dir, repair, submits, total)
                whole_process_with_LLM(project_dir, test_num, context, submits, total)
                break
            break
        
        # Print the modified Java test method
        # print(replaced_assertions_per_method)
            

    with open(project_dir + testsdb_file, 'w') as json_file:
        json.dump(class_results, json_file, indent=4)  # Use indent for pretty formatting (optional)

    
    
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
