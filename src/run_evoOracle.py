import os.path
import time
from db_operations import *
from tools import *
from parse_data import parse_data
from export_data import export_data
from scope_test import start_generation, prepare_test_cases
from parse_xml import result_analysis
from task import Task

def clear_dataset():
    """
    Clear the dataset folder.
    :return: None
    """
    # Delete the dataset folder
    if os.path.exists(dataset_dir):
        shutil.rmtree(dataset_dir)

def run():
    # Clear previous entries from DB
    # drop_table()

    # Create the table
    # create_table()

    # Parse project
    info_path = Task.parse(project_dir)

    # Parse data
    parse_data(info_path, db_file)

    # clear last dataset
    # clear_dataset()

    # # Export data for multi-process
    # export_data()

    project_name = os.path.basename(os.path.normpath(project_dir))

    # SQL query to get the classes that contains tests.
    sql_query = """
    SELECT id, class_name, class_path, signature, super_class, package, imports, fields, has_constructor, contains_test, dependencies 
    FROM class where contains_test is true AND project_name='{}';
    """.format(project_name)

    # Start the whole process
    # prepare_test_cases(sql_query, multiprocess=False, repair=True, confirmed=False)

    # Export the result
    # result_analysis()



if __name__ == '__main__':
    run()