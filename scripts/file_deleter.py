import os

def read_string_list(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def rename_matching_files(directory, string_list):
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            for string_to_match in string_list:
                if string_to_match in file_name and ".failed" not in file_name:
                    old_path = os.path.join(root, file_name)
                    new_name = file_name + ".failed"
                    new_path = os.path.join(root, new_name)
                    os.rename(old_path, new_path)
                    print(f'Renamed: {file_name} to {new_name}')

if __name__ == "__main__":
    directory_to_search = "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/"
    string_list_file = "/home/shaker/Documents/delete_me.txt"

    strings_to_match = read_string_list(string_list_file)
    rename_matching_files(directory_to_search, strings_to_match)
