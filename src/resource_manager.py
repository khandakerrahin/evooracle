import json
from tools import *

class ResourceManager:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.data = self.load_json()

    def load_json(self):
        with open(self.json_file_path, 'r') as json_file:
            return json.load(json_file)

    def get_entries_with_contains_test(self, project_name):
        filtered_entries = []
        for entry in self.data:
            if entry.get('project_name') == project_name and entry.get('contains_test'):
                filtered_entries.append(entry)
        return filtered_entries

    def get_entries_without_contains_test(self, project_name):
        filtered_entries = []
        for entry in self.data:
            if entry.get('project_name') == project_name and not entry.get('contains_test'):
                filtered_entries.append(entry)
        return filtered_entries
    
    def get_methods_by_project_and_class(self, project_name, class_name):
        methods = []
        for entry in self.data:
            if entry.get('project_name') == project_name and entry.get('class_name') == class_name:
                methods.extend(entry.get('methods', []))
        return methods
    
# Example usage:
if __name__ == '__main__':
    json_file_path = db_file  # Replace with the actual file path
    manager = ResourceManager(json_file_path)

    project_name_to_query = 'lang_1_buggy'  # Replace with the project name you want to query
    # entries_with_contains_test = manager.get_entries_with_contains_test(project_name_to_query)
    # entries_without_contains_test = manager.get_entries_without_contains_test(project_name_to_query)
    

    class_name_to_query = 'NumberUtils_ESTest'

    methods_for_project_and_class = manager.get_methods_by_project_and_class(project_name_to_query, class_name_to_query)

    print("Methods for Project and Class:")
    for method in methods_for_project_and_class:
        print(method.get('method_name'), method.get("parameters"))
