import os.path
import time
import sys  # Import the sys module to access command-line arguments
from db_operations import *
from tools import *
from parse_data import parse_data
from export_data import export_data
from test_processor import prepare_test_cases_entries, start_generation, prepare_test_cases
from parse_xml import result_analysis
from task import Task
from colorama import Fore, Style, init

def clear_dataset(project_dir):
    """
    Clear the dataset folder.
    :return: None
    """
    ds_dir = project_dir + dataset_dir
    # Delete the dataset folder
    if os.path.exists(ds_dir):
        shutil.rmtree(ds_dir)

def run(test_id, project_dir, class_name, method_name, llm_name):
    # Start the whole process
    prepare_test_cases(test_id, project_dir, class_name, method_name, llm_name)
    

if __name__ == '__main__':
    project_dir = default_project_dir
    # Check if a command-line argument (project_dir) is provided
    if len(sys.argv) > 5:
        test_id = sys.argv[1]
        project_dir = sys.argv[2]
        class_name = sys.argv[3]
        method_name = sys.argv[4]
        llm_name = sys.argv[5]
        
        run(test_id, project_dir, class_name, method_name, llm_name)
    else:
        print(Fore.RED + "Run failed, missing arguments.", Style.RESET_ALL)        
    
