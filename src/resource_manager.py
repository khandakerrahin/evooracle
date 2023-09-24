import json
from tools import *

class ResourceManager:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.data = self.load_json()

    def load_json(self):
        with open(self.json_file_path, 'r') as json_file:
            return json.load(json_file)

    def get_class_details_from_projectname_classname(self, project_name, class_name):
        filtered_entries = []
        for entry in self.data:
            if entry.get('project_name') == project_name and entry.get('class_name') == class_name:
                return entry
        return filtered_entries
    
    def get_classes_with_contains_test(self, project_name):
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
    
    def get_details_by_project_class_and_method(self, project_name, class_name, method_name, onlyEssentials):
        for entry in self.data:
            if (
                entry.get('project_name') == project_name
                and entry.get('class_name') == class_name
            ):
                class_methods = entry.get('methods', [])
                for method in class_methods:
                    if method.get('method_name') == method_name:
                        if onlyEssentials:
                            # get only the essentials
                            details = {
                                "signature": method.get("signature"),
                                "parameters": method.get("parameters"),
                                "dependencies": method.get("dependencies"),
                                "return_type": method.get("return_type")
                            }
                            return details
                        else:
                            # get all details
                            return method
                    
        # print("method_details : "+ str(method_details))               
        return None

    def get_package_by_project_and_class(self, project_name, class_name):
        for entry in self.data:
            if (
                entry.get('project_name') == project_name
                and entry.get('class_name') == class_name
                and 'package' in entry
            ):
                package_declaration = entry['package']
                package_name = package_declaration.split(' ')[1].strip(';')
                return package_name
        return None
    
# Example usage:
if __name__ == '__main__':
    manager = ResourceManager(db_file)

    project_name_to_query = 'lang_1_buggy'  # Replace with the project name you want to query
    
    class_name_to_query = 'NumberUtils_ESTest'
    method_name_to_query = 'test111'


    class_name_to_query = 'NumberUtils'
    method_name_to_query = 'min'

    # print("Methods for Project and Class:")
    # for method in methods_for_project_and_class:
    #     print(method.get('method_name'), method.get("parameters"))

    method_details = manager.get_details_by_project_class_and_method(
        project_name_to_query, class_name_to_query, method_name_to_query
    )

    if method_details:
        print("Method Details:")
        
        for method in method_details:
            for key, value in method.items():
                print(f"{key}: {value}")
    else:
        print(f"No details found for method '{method_name_to_query}' in class '{class_name_to_query}' of project '{project_name_to_query}'.")