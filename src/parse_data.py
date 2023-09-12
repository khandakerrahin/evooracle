"""
This file is for parsing the .json data.
And insert them into Current Database.

Author: Xie zhuokui
Date: 2023-04-01
"""

import json
import os
from db_operations import database


def parse_data(dir_path: str, db_out_path: str):
    """
    Parse the data from .json files.
    :param dir_path: the path of the .json files.
    :return: None
    """
    # db = database()
    
    # Create a list to store the extracted class data
    class_data_to_store = []
    
    for root, dirs, files in os.walk(dir_path):
        
        for filename in files:
            if filename.endswith('.json'):
                with open(os.path.join(root, filename), "r") as f:
                    json_data = json.load(f)

                for class_data in json_data:
                    # Get class data
                    project_name = class_data['project_name']
                    class_name = class_data['class_name']
                    interfaces = class_data['interfaces']
                    class_path = class_data['class_path']
                    c_sig = class_data['c_sig']

                    method_data_to_store = []
                        
                    if class_data['superclass']:
                        super_class = class_data['superclass'].split(' ')[1]
                    else:
                        super_class = ""

                    if class_data['imports']:
                        imports = "\n".join(class_data['imports'])
                    else:
                        imports = ""

                    if "package" in class_data:
                        package = class_data["package"]
                    else:
                        package = ""

                    has_constructor = class_data['has_constructor']
                    argument_list = class_data['argument_list']
                    contains_test = class_data['contains_test']

                    # Get field data
                    fields = []
                    for field in class_data['fields']:
                        if field['original_string'] not in fields:
                            fields.append(field['original_string'])
                    fields = "\n".join(fields)

                    # Will append from all constructors
                    c_deps = {}

                    # Get method data
                    methods = class_data['methods']
                    focal_method_names = ''
                    
                    for method_data in methods:
                        m_sig = method_data['m_sig']
                        method_name = method_data['method_name']
                        source_code = method_data['source_code']
                        use_field = method_data['use_field']
                        parameters = method_data['parameters']
                        is_test_method = method_data['is_test_method']

                        if is_test_method:
                            focal_method_names = method_data['focal_methods']
                        
                        if "public" in method_data['modifiers']:
                            is_public = True
                        else:
                            is_public = False
                        is_constructor = method_data['is_constructor']
                        is_get_set = method_data['is_get_set']
                        m_deps = method_data['m_deps']
                        return_type = method_data['return']

                        # Add dependencies from constructor
                        if is_constructor:
                            for dep_class in m_deps:
                                if dep_class not in c_deps:
                                    c_deps[dep_class] = []
                                c_deps[dep_class].append(m_deps[dep_class])

                        # insert method data into table method
                        # db.insert("method", row={"project_name": project_name,
                        #                         "signature": m_sig,
                        #                         "method_name": method_name,
                        #                         "focal_method_name":str(focal_method_names),
                        #                         "parameters": parameters,
                        #                         "source_code": source_code,
                        #                         "source_code_with_placeholder": "",
                        #                         "class_name": class_name,
                        #                         "dependencies": str(m_deps),
                        #                         "use_field": use_field,
                        #                         "is_constructor": is_constructor,
                        #                         "is_test_method": is_test_method,
                        #                         "is_get_set": is_get_set,
                        #                         "is_public": is_public})
                        
                        # store method data into json
                        method_entry={
                                "project_name": project_name,
                                "signature": m_sig,
                                "method_name": method_name,
                                "focal_method_name":str(focal_method_names),
                                "parameters": parameters,
                                "source_code": source_code,
                                "source_code_with_placeholder": "",
                                "class_name": class_name,
                                "dependencies": str(m_deps),
                                "use_field": use_field,
                                "is_constructor": is_constructor,
                                "is_test_method": is_test_method,
                                "is_get_set": is_get_set,
                                "is_public": is_public,
                                "return_type": return_type
                            }
                        
                        method_data_to_store.append(method_entry)


                    # insert class data into table class
                    # db.insert("class", row={"project_name": project_name,
                    #                         "class_name": class_name,
                    #                         "class_path": class_path,
                    #                         "signature": c_sig,
                    #                         "super_class": super_class,
                    #                         "package": package,
                    #                         "imports": imports,
                    #                         "fields": fields,
                    #                         "has_constructor": has_constructor,
                    #                         "contains_test":contains_test,
                    #                         "dependencies": str(c_deps)})

                    # store class data into json
                    class_entry = {
                                "project_name": project_name,
                                "class_name": class_name,
                                "class_path": class_path,
                                "signature": c_sig,
                                "super_class": super_class,
                                "interfaces": interfaces,
                                "package": package,
                                "imports": imports,
                                "fields": fields,
                                "argument_list": argument_list,
                                "methods":method_data_to_store,
                                "has_constructor": has_constructor,
                                "contains_test":contains_test,
                                "dependencies": str(c_deps)
                            }
                    
                    class_data_to_store.append(class_entry)

                    print(class_name, "FINISHED!")
                    break
                
                # Create the directory if it does not exist
                output_dir = os.path.dirname(db_out_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                # Write the list of parsed data to a JSON file
                with open(db_out_path, "w") as json_output:
                    json.dump(class_data_to_store, json_output, indent=4)

if __name__ == '__main__':
    print("This action will alter the information in database.")
    confirm = input("Are you sure to parse the data? (y/n) ")
    if confirm == "y":
        parse_data("/Users/chenyi/Desktop/ChatTester/TestGPT_ASE/information/Lang")
    else:
        print("Canceled.")
