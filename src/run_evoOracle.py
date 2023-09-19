import os.path
import time
import sys  # Import the sys module to access command-line arguments
from db_operations import *
from tools import *
from parse_data import parse_data
from export_data import export_data
from test_processor import start_generation, prepare_test_cases
from parse_xml import result_analysis
from task import Task

def clear_dataset(project_dir):
    """
    Clear the dataset folder.
    :return: None
    """
    ds_dir = project_dir + dataset_dir
    # Delete the dataset folder
    if os.path.exists(ds_dir):
        shutil.rmtree(ds_dir)

def run(project_dir):
    
    # Clear previous entries from DB
    # drop_table()

    # Create the table
    # create_table()

    # Parse project
    info_path = Task.parse(project_dir)

    # # Parse data
    parse_data(info_path, (project_dir+db_file))

    # clear last dataset
    # clear_dataset()

    # # Export data for multi-process
    # export_data()

    project_name = os.path.basename(os.path.normpath(project_dir))

    # Start the whole process
    prepare_test_cases(project_dir)

    # Export the result
    # result_analysis()

if __name__ == '__main__':
    project_dir = default_project_dir
    # Check if a command-line argument (project_dir) is provided
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]

        
    run(project_dir)
