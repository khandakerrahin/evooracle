import copy
import csv
import os.path
import sys
import time
import openai
from tools import *
import random
import concurrent.futures
import javalang
import jinja2
from colorama import Fore, Style, init
from task import Task
import time


# Import depdencies 
from langchain.llms import GPT4All, OpenAI
from langchain import PromptTemplate, LLMChain
from ctransformers.langchain import CTransformers

# Python toolchain imports 
from langchain.agents.agent_toolkits import create_python_agent
from langchain.tools.python.tool import PythonREPLTool
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

init()
# Create a jinja2 environment
env = jinja2.Environment(loader=jinja2.FileSystemLoader('../prompt'))

# BASE_PATH = '/home/shaker/models/GPT4All/'
BASE_PATH = LLM_BASE_PATH
# PATH = f'{BASE_PATH}{"ggml-gpt4all-l13b-snoozy.bin"}'
PATH = f'{BASE_PATH}{sys.argv[5]}'

# Callbacks support token-wise streaming
callbacks = [StreamingStdOutCallbackHandler()]

llm = GPT4All(model=PATH, backend="gptj", callbacks=callbacks, verbose=True, temp=temperature, n_predict=n_predict, top_p=top_p, top_k=top_k, n_batch=n_batch, repeat_penalty=repeat_penalty, repeat_last_n=repeat_last_n)

template = PromptTemplate(input_variables=['action'], template="""{action}""")
chain = LLMChain(llm=llm, prompt=template, verbose=True) 

def ask_openLLM(messages):
    # return "failed"
    # return 'assertTrue(nodeInstaller4.getNodeVersion().equals("/node"));\n  assertFalse(nodeInstaller4.getNodeVersion().equals("/node"));\n  assertSame(nodeInstaller4.getNodeVersion().equals("/node"));'
    # Retry 5 times when error occurs
    max_try = 5
    while max_try:
        try:
            completion = chain.run(messages)
            return completion
        except Exception as e:
            print(Fore.RED + str(e), Style.RESET_ALL)
        max_try -= 1
    return ""

def ask_chatgpt(messages, save_path):
    """
    Send messages to GPT, and save its response.
    :param messages: The messages to send to OpenAI.
    :param save_path: The path to save the result.
    :return: [{"role":"user","content":"..."}]
    """
    # Send a request to OpenAI
    # Max prompt token exceeded, no need to send request.
    if get_messages_tokens(messages) > MAX_PROMPT_TOKENS:
        return False
    openai.api_key = random.choice(api_keys)
    # Retry 5 times when error occurs
    max_try = 5
    while max_try:
        try:
            completion = openai.ChatCompletion.create(messages=messages,
                                                      model=model,
                                                      temperature=temperature,
                                                      top_p=top_p,
                                                      frequency_penalty=frequency_penalty,
                                                      presence_penalty=presence_penalty)
            with open(save_path, "w") as f:
                json.dump(completion, f)
            return True
        except Exception as e:
            print(Fore.RED + str(e), Style.RESET_ALL)
            if "This model's maximum context length is 4097 tokens." in str(e):
                break
            time.sleep(10)
            # If rate limit reached we wait a random sleep time
            if "Rate limit reached" in str(e):
                sleep_time = random.randint(60, 120)
                time.sleep(sleep_time)
        max_try -= 1
    return False


def generate_prompt(template_name, context: dict):
    """
    Generate prompt via jinja2 engine
    :param template_name: the name of the prompt template
    :param context: the context to render the template
    :return:
    """
    # Load template
    template = env.get_template(template_name)
    prompt = template.render(context)

    return prompt


def load_context_file(context_file):
    if isinstance(context_file, str):
        with open(context_file, "r") as f:
            return json.load(f)
    return context_file


def generate_messages(template_name, context):
    """
    This function generates messages before asking LLM, using templates.
    :param template_name: The template name of the user template.
    :param context: The context JSON file or dict to render the template.
    :return: A list of generated messages.
    """
    message = generate_prompt(template_name, context)
    
    return message


def complete_code(code):
    """
    To complete the code
    :param code:
    :return:
    """

    # We delete the last incomplete test.
    code = code.split("@Test\n")
    code = "@Test\n".join(code[:-1]) + '}'
    return code


def process_error_message(error_message, allowed_tokens):
    """
    Process the error message
    :param error_message:
    :param allowed_tokens:
    :return:
    """
    if allowed_tokens <= 0:
        return ""
    while count_tokens(error_message) > allowed_tokens:
        if len(error_message) > 50:
            error_message = error_message[:-50]
        else:
            break
    return error_message


def if_code_is_valid(code) -> bool:
    """
    Check if the code is valid
    :param code:
    :return: True or False
    """
    if "{" not in code or "}" not in code:
        return False
    try:
        javalang.parse.parse(code)
        return True
    except Exception:
        return False


def syntactic_check(code):
    """
    Syntactic repair
    :param code:
    :return: has_syntactic_error, code
    """
    if is_syntactic_correct(code):
        return False, code
    else:
        stop_point = [";", "}", "{", " "]  # Stop point
        for idx in range(len(code) - 1, -1, -1):
            if code[idx] in stop_point:
                code = code[:idx + 1]
                break
        left_bracket = code.count("{")
        right_bracket = code.count("}")
        for idx in range(left_bracket - right_bracket):
            code += "}\n"

        if is_syntactic_correct(code):
            return True, code

        matches = list(re.finditer(r"(?<=\})[^\}]+(?=@)", code))
        if matches:
            code = code[:matches[-1].start() + 1]
            left_count = code.count("{")
            right_count = code.count("}")
            for _ in range(left_count - right_count):
                code += "\n}"
        if is_syntactic_correct(code):
            return True, code
        else:
            return True, ""


def is_syntactic_correct(code):
    """
    Check if the code is syntactically correct
    :param code:
    :return:
    """
    try:
        javalang.parse.parse(code)
        return True
    except Exception as e:
        return False


def extract_code(string):
    """
    Check if the string is valid code and extract it.
    :param string:
    :return: has_code, extracted_code, has_syntactic_error
    """
    # if the string is valid code, return True
    if is_syntactic_correct(string):
        return True, string, False

    has_code = False
    extracted_code = ""
    has_syntactic_error = False

    # Define regex pattern to match the code blocks
    pattern = r"```[java]*([\s\S]*?)```"

    # Find all matches in the text
    matches = re.findall(pattern, string)
    if matches:
        # Filter matches to only include ones that contain "@Test"
        filtered_matches = [match.strip() for match in matches if
                            "@Test" in match and "class" in match and "import" in match]
        if filtered_matches:
            for match in filtered_matches:
                has_syntactic_error, extracted_code = syntactic_check(match)
                if extracted_code != "":
                    has_code = True
                    break

    if not has_code:
        if "```java" in string:
            separate_string = string.split("```java")[1]
            if "@Test" in separate_string:
                has_syntactic_error, temp_code = syntactic_check(separate_string)
                if temp_code != "":
                    extracted_code = temp_code
                    has_code = True
        elif "```" in string:
            separate_strings = string.split("```")
            for separate_string in separate_strings:
                if "@Test" in separate_string:
                    has_syntactic_error, temp_code = syntactic_check(separate_string)
                    if temp_code != "":
                        extracted_code = temp_code
                        has_code = True
                        break
        else:  # Define boundary
            allowed = ["import", "packages", "", "@"]
            code_lines = string.split("\n")
            start, anchor, end = -1, -1, -1
            allowed_lines = [False for _ in range(len(code_lines))]
            left_brace = {x: 0 for x in range(len(code_lines))}
            right_brace = {x: 0 for x in range(len(code_lines))}
            for i, line in enumerate(code_lines):
                left_brace[i] += line.count("{")
                right_brace[i] += line.count("}")
                striped_line = line.strip()

                for allow_start in allowed:
                    if striped_line.startswith(allow_start):
                        allowed_lines[i] = True
                        break

                if re.search(r'public class .*Test', line) and anchor == -1:
                    anchor = i

            if anchor != -1:
                start = anchor
                while start:
                    if allowed_lines[start]:
                        start -= 1

                end = anchor
                left_sum, right_sum = 0, 0
                while end < len(code_lines):
                    left_sum += left_brace[end]
                    right_sum += right_brace[end]
                    if left_sum == right_sum and left_sum >= 1 and right_sum >= 1:
                        break
                    end += 1

                temp_code = "\n".join(code_lines[start:end + 1])
                has_syntactic_error, temp_code = syntactic_check(temp_code)
                if temp_code != "":
                    extracted_code = temp_code
                    has_code = True

    extracted_code = extracted_code.strip()
    return has_code, extracted_code, has_syntactic_error


def extract_and_run(evooracle_source_code, evosuite_source_code, output_path, class_name, test_num, method_name, project_name, package, project_dir):
    """
    Extract the code and run it
    :param project_name:
    :param test_num:
    :param method_id:
    :param class_name:
    :param input_string:
    :param output_path:
    :return:
    """
    result = {}
    evo_result = {
        "eo_is_compiled": False,
        "eo_is_run": False,
        "eo_mutation_score": 0,
        "es_is_compiled": False,
        "es_is_run": False,
        "es_mutation_score": 0,
        "prompts_and_responses": None,
    }

    # 1. Extract the code
    has_code, extracted_code, has_syntactic_error = extract_code(evooracle_source_code)
    if not has_code:
        return evo_result
    result["has_code"] = has_code
    result["source_code"] = extracted_code
    if package:
        result["source_code"] = repair_package(extracted_code, package)
    result["has_syntactic_error"] = has_syntactic_error
    # 2. Run the code
    temp_dir = os.path.join(os.path.dirname(output_path), "temp")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # print("Project Name: " + project_name)
    # print("Class Name: " + class_name)

    out_dir = os.path.dirname(os.path.dirname(output_path))

    renamed_class_evooracle = class_name + '_' + str(test_num) + string_tables.EVOORACLE_SIGNATURE
    renamed_class_source_code_evooracle = change_class_name(extracted_code, class_name, renamed_class_evooracle)

    evooracle_test_file_name = export_method_test_case(out_dir, renamed_class_evooracle, renamed_class_source_code_evooracle)
    
    renamed_class_evosuite = class_name + '_' + str(test_num) + string_tables.EVOSUITE_UNIT_SIGNATURE
    renamed_class_source_code_evosuite = change_class_name(evosuite_source_code, class_name, renamed_class_evosuite)
    
    evosuite_test_file_name = export_method_test_case(out_dir, renamed_class_evosuite, renamed_class_source_code_evosuite)
    
    # run test
    response_dir = os.path.abspath(out_dir)
    target_dir = os.path.abspath(project_dir)

    # print("response_dir: " + response_dir)
    # print("target_dir: " + target_dir)
    # print("test_file_name: " + test_file_name)

    test_result_eo_c, test_result_eo_r, test_result_eo_ms = Task.test(response_dir, target_dir, evooracle_test_file_name, package, renamed_class_evooracle)
    test_result_es_c, test_result_es_r, test_result_es_ms = Task.test(response_dir, target_dir, evosuite_test_file_name, package, renamed_class_evosuite)

    # 3. Read the result
    evo_result["eo_is_compiled"] = test_result_eo_c
    evo_result["eo_is_run"] = test_result_eo_r
    evo_result["eo_mutation_score"] = test_result_eo_ms

    evo_result["es_is_compiled"] = test_result_es_c
    evo_result["es_is_run"] = test_result_es_r
    evo_result["es_mutation_score"] = test_result_es_ms
    
    return evo_result


def remain_prompt_tokens(messages):
    return MAX_PROMPT_TOKENS - get_messages_tokens(messages)


def whole_process_with_LLM(project_dir, context, test_id, llm_name, consider_dev_comments):
    """
    start_generation
    :param project_dir:
    :param context:
    :param test_id:
    :return:
    """

    project_name = context.get("project_name")
    test_class_name = context.get("test_class_name")
    test_class_path = context.get("test_class_path")
    method_name = context.get("method_name")
    
    # context = {"project_name", "class_name", "test_class_path", "test_class_name", "test_method_name", "method_name", 
    #               "method_details", "test_method_code", "assertion_placeholder", "test_case_with_placeholder", "package", "evosuite_test_case", "developer_comments"}

    # Create subdirectories for each test
    save_dir = os.path.join(os.path.dirname(test_class_path), str(test_id))
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    steps, rounds = 0, 0

    # Get the current time in milliseconds
    start_time = time.perf_counter()
    
    result = {
                "attempts": 0, 
                "assertion_generated": False,
                "assertion_generation_time": 0,
                "eo_is_compiled": False,
                "eo_is_run": False,
                "eo_mutation_score": 0,
                "eo_assertions": None,
                "es_is_compiled": False,
                "es_is_run": False,
                "es_mutation_score": 0,
                "prompts_and_responses": None,
            }
    
    prompts_and_responses = []

    # if consider_dev_comments:
    #     prompt_template = TEMPLATE_WITH_DEV_COMMENTS
    # else:
    #     prompt_template = TEMPLATE_BASIC

    prompt_template = TEMPLATE_BASIC

    if not consider_dev_comments:
        context["method_details"] = remove_key_value_pair_from_json(context.get("method_details"), "dev_comments")

        # print("AFTER REMOVING DEV COMMENTS:")
        # print(context["method_details"])
    
    try:
        while rounds < max_attempts:
            # 1. Ask LLM
            steps += 1
            rounds += 1
            # print(method_name, "test_" + str(test_id), "Asking " + llm_name + "...", "rounds", rounds)
            print("test_" + str(test_id), "Asking " + llm_name + "...", "rounds", rounds)

            # context = {"project_name", "class_name", "test_class_path", "test_class_name", "test_method_name", "method_name", 
            #           "method_details", "test_method_code", "assertion_placeholder", "test_case_with_placeholder", "package", "evosuite_test_case", "developer_comments"
            
            
            # if rounds > 2:
            #     # Third round : super trimmed prompt
            #     trimmed_context = context

            #     if len(context.get("developer_comments")) > 500:
            #         trimmed_context["developer_comments"] = trim_string_to_desired_length(context.get("developer_comments"), 500)
            #     elif len(context.get("developer_comments")) > 300:
            #         trimmed_context["developer_comments"] = trim_string_to_desired_length(context.get("developer_comments"), 300)

            #     trimmed_context["test_method_code"] = trim_string_to_substring(context.get("test_method_code"), string_tables.ASSERTION_PLACEHOLDER)
            #     messages = generate_messages(prompt_template, trimmed_context)
            # if rounds > 1:
            #     # Second round : trimmed prompt
            #     trimmed_context = context
            #     if len(context.get("developer_comments")) > 500:
            #         trimmed_context["developer_comments"] = trim_string_to_desired_length(context.get("developer_comments"), 500)
            #     elif len(context.get("developer_comments")) > 300:
            #         trimmed_context["developer_comments"] = trim_string_to_desired_length(context.get("developer_comments"), 300)

            #     trimmed_context["test_method_code"] = trim_string_to_substring(context.get("test_method_code"), string_tables.ASSERTION_PLACEHOLDER)
            #     messages = generate_messages(prompt_template, trimmed_context)
            # else:
            #     # first round : normal prompt
            #     messages = generate_messages(prompt_template, context)

            # print(Fore.BLUE, messages, Style.RESET_ALL)

            if rounds > 2:
                # Third round : super trimmed prompt
                trimmed_context = context

                if len(context.get("method_details")) > 3:
                    trimmed_context["method_details"] = trim_list_to_desired_size(context.get("method_details"), 3)
                elif len(context.get("method_details")) > 2:
                    trimmed_context["method_details"] = trim_list_to_desired_size(context.get("method_details"), 2)

                trimmed_context["test_method_code"] = trim_string_to_substring(context.get("test_method_code"), string_tables.ASSERTION_PLACEHOLDER)
                messages = generate_messages(prompt_template, trimmed_context)
            if rounds > 1:
                # Second round : trimmed prompt
                trimmed_context = context
                if len(context.get("method_details")) > 5:
                    trimmed_context["method_details"] = trim_list_to_desired_size(context.get("method_details"), 5)
                elif len(context.get("method_details")) > 3:
                    trimmed_context["method_details"] = trim_list_to_desired_size(context.get("method_details"), 3)

                trimmed_context["test_method_code"] = trim_string_to_substring(context.get("test_method_code"), string_tables.ASSERTION_PLACEHOLDER)
                messages = generate_messages(prompt_template, trimmed_context)
                
            else:
                # first round : normal prompt
                messages = generate_messages(prompt_template, context)
                
            # print("Prompt: " + Fore.YELLOW + messages, Style.RESET_ALL)  

            print("Attempt: " + Fore.YELLOW + str(rounds), Style.RESET_ALL)  
            llm_result = ask_openLLM(messages)

            prompts_and_responses.append({"prompt":messages,"response":llm_result})
            
            steps += 1

            raw_file_name = os.path.join(save_dir, str(steps) + "_raw_" + str(rounds) + ".json")

            assertions = extract_first_assertion_from_string(llm_result)
            
            if assertions:
                print("Assertion generate: " + Fore.GREEN + "SUCCESS", Style.RESET_ALL)
                # print("LLM Response Assertion: " + Fore.GREEN + assertions, Style.RESET_ALL)
                # print()
                
                end_time = time.perf_counter()

                if not assertions.endswith(";"):
                    assertions += ";"

                evooracle_source_code = re.sub(re.escape(string_tables.ASSERTION_PLACEHOLDER), assertions, context.get("test_case_with_placeholder"))
                evosuite_source_code = context.get("evosuite_test_case")
                # print("Updated test source code:")
                # print(updated_source_code)
                
                evo_result = extract_and_run(evooracle_source_code, evosuite_source_code, raw_file_name, test_class_name, test_id, context.get("method_name"),
                                                        project_name, context.get("package"), project_dir)
                
                result["assertion_generated"] = True
                result["eo_is_compiled"] = evo_result["eo_is_compiled"]
                result["eo_is_run"] = evo_result["eo_is_run"]
                result["eo_mutation_score"] = evo_result["eo_mutation_score"]
                result["eo_assertions"] = assertions
                
                result["es_is_compiled"] = evo_result["es_is_compiled"]
                result["es_is_run"] = evo_result["es_is_run"]
                result["es_mutation_score"] = evo_result["es_mutation_score"]
                
                break
            else:
                print("Assertion generate: " + Fore.RED + "FAILED", Style.RESET_ALL)
                end_time = time.perf_counter()
        
        result["attempts"] = rounds

    except Exception as e:
        print(Fore.RED + str(e), Style.RESET_ALL)
        end_time = time.perf_counter()
    
    # end_time = time.perf_counter()

    assertion_generation_time = (end_time - start_time) * 1000

    result["assertion_generation_time"] = assertion_generation_time
    result["prompts_and_responses"] = prompts_and_responses

    return result

def trim_string_to_substring(original_string, substring):
    # Find the index of the substring
    substring_index = original_string.find(substring)

    if substring_index != -1:
        # Trim the string to keep everything before and including the substring
        trimmed_string = original_string[:substring_index + len(substring)]
    else:
        # Substring not found, keep the original string as is
        trimmed_string = original_string

    return trimmed_string

def trim_string_to_desired_length(original_string, cutoff_length):
    # Trim the string
    trimmed_string = original_string[:cutoff_length]

    # Print the trimmed string
    print(trimmed_string)

    return trimmed_string

def trim_list_to_desired_size(original_list, cutoff_length):
    try:
        if not isinstance(original_list, list):
            original_list = json.loads(original_list)
        
        while len(original_list) > cutoff_length:
            original_list.pop()  
        return original_list
    except json.JSONDecodeError:
        return original_list

def whole_process(test_num, base_name, base_dir, repair, submits, total):
    """
    Multiprocess version of start_generation
    :param test_num:
    :param base_name:
    :param base_dir:
    :param repair:
    :param submits:
    :param total:
    :return:
    """
    progress = '[' + str(submits) + ' / ' + str(total) + ']'
    # Create subdirectories for each test
    save_dir = os.path.join(base_dir, str(test_num))
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    run_temp_dir = os.path.join(save_dir, "runtemp")

    steps, rounds = 0, 0
    method_id, project_name, class_name, method_name = parse_file_name(base_name)

    # 1. Get method data
    with open(get_dataset_path(method_id, project_name, class_name, method_name, "raw"), "r") as f:
        raw_data = json.load(f)

    package = raw_data["package"]
    imports = raw_data["imports"]

    # 2. Get data from direction_1 as well as direction_3
    with open(get_dataset_path(method_id, project_name, class_name, method_name, 1), "r") as f:
        context_d_1 = json.load(f)
        print(context_d_1)
    with open(get_dataset_path(method_id, project_name, class_name, method_name, 3), "r") as f:
        context_d_3 = json.load(f)
        print(context_d_3)

    def _remove_imports_context(strings):
        if imports:
            strings = strings.replace(imports, "")
        if package:
            strings = strings.replace(package, "")
        strings = strings.strip()
        return strings

    try:
        while rounds < max_attempts:
            # 1. Ask LLM
            steps += 1
            rounds += 1
            print(progress, method_id, "test_" + str(test_num), "Asking " + model + "...", "rounds", rounds)
            llm_file_name = os.path.join(save_dir, str(steps) + "_LLM_" + str(rounds) + ".json")
            # Need to generate new messages
            if rounds != 1:
                last_round_result = get_latest_file(save_dir)
                with open(last_round_result, "r") as f:
                    last_round_result = json.load(f)
                last_raw = get_latest_file(save_dir, suffix="raw")
                with open(last_raw, "r") as f:
                    last_raw = json.load(f)

                # Prepare the error message
                context = {"class_name": context_d_1["class_name"], "method_name": context_d_1["focal_method"],
                           "unit_test": last_raw["source_code"], "method_code": context_d_1["information"]}
                # Required, cannot truncate

                # Adaptive generate error message
                messages = generate_messages(TEMPLATE_ERROR, context)
                allow_tokens = remain_prompt_tokens(messages)
                if allow_tokens < MIN_ERROR_TOKENS:
                    context["method_code"] = _remove_imports_context(context["method_code"])
                    messages = generate_messages(TEMPLATE_ERROR, context)
                    allow_tokens = remain_prompt_tokens(messages)
                if allow_tokens < MIN_ERROR_TOKENS:
                    context["method_code"] = context_d_3["full_fm"]
                    messages = generate_messages(TEMPLATE_ERROR, context)
                    allow_tokens = remain_prompt_tokens(messages)
                if allow_tokens < MIN_ERROR_TOKENS:
                    context["method_code"] = _remove_imports_context(context_d_3["full_fm"])
                    messages = generate_messages(TEMPLATE_ERROR, context)
                    allow_tokens = remain_prompt_tokens(messages)
                if allow_tokens >= MIN_ERROR_TOKENS:
                    if "compile_error" in last_round_result:
                        context["error_type"] = "compiling"
                        error_mes = process_error_message(last_round_result["compile_error"], allow_tokens)
                        context["error_message"] = error_mes
                    if "runtime_error" in last_round_result:
                        context["error_type"] = "running"
                        error_mes = process_error_message(last_round_result["runtime_error"], allow_tokens)
                        context["error_message"] = error_mes
                else:
                    print(progress, Fore.RED + method_id, "Tokens not enough, test fatal error...",
                          Style.RESET_ALL)  # Fatal error
                    break
                if "compile_error" not in last_round_result and "runtime_error" not in last_round_result:
                    print(progress, Fore.RED + method_id, "Timeout error, test fatal error...", Style.RESET_ALL)
                    break
                messages = generate_messages(TEMPLATE_ERROR, context)
                # print('-------------------')
                # print(context["error_message"])
            else:  # Direction_1 or Direction_3
                if not context_d_3["c_deps"] and not context_d_3["m_deps"]:  # No dependencies d_1
                    context = copy.deepcopy(context_d_1)
                    messages = generate_messages(TEMPLATE_NO_DEPS, context)
                    if remain_prompt_tokens(messages) < 0:  # Truncate information
                        context["information"] = _remove_imports_context(context["information"])
                        messages = generate_messages(TEMPLATE_NO_DEPS, context)
                        if remain_prompt_tokens(messages) < 0:  # Failed generating messages
                            messages = []
                else:  # Has dependencies d_3
                    context = copy.deepcopy(context_d_3)
                    messages = generate_messages(TEMPLATE_WITH_DEPS, context)
                    if remain_prompt_tokens(messages) < 0:  # Need Truncate information
                        context["full_fm"] = _remove_imports_context(context["full_fm"])
                        messages = generate_messages(TEMPLATE_WITH_DEPS, context)
                        if remain_prompt_tokens(messages) < 0:  # Failed generating messages
                            messages = []

                if not messages:  # Turn to minimum messages
                    context = copy.deepcopy(context_d_1)  # use direction 1 as template
                    context["information"] = context_d_3["full_fm"]  # use full_fm d_3 as context
                    messages = generate_messages(TEMPLATE_NO_DEPS, context)
                    if remain_prompt_tokens(messages) < 0:
                        context["information"] = _remove_imports_context(context["information"])
                        messages = generate_messages(TEMPLATE_NO_DEPS, context)  # !! MINIMUM MESSAGES!!
                        if remain_prompt_tokens(messages) < 0:  # Failed generating messages
                            print(progress, Fore.RED + "Tokens not enough, test fatal error...", Style.RESET_ALL)
                            break
                # print(Fore.BLUE, messages[1]['content'], Style.RESET_ALL)

            print(Fore.BLUE, messages, Style.RESET_ALL)
            
            # status = ask_chatgpt(messages, llm_file_name)
            status = ask_openLLM(messages, llm_file_name)
            
            if not status:
                print(progress, Fore.RED + 'LLM Failed processing messages', Style.RESET_ALL)
                break

            with open(llm_file_name, "r") as f:
                gpt_result = json.load(f)

            # 2. Extract information from LLM, and RUN save the result
            steps += 1

            raw_file_name = os.path.join(save_dir, str(steps) + "_raw_" + str(rounds) + ".json")

            # extract the test and save the result in raw_file_name
            # input_string = gpt_result["choices"][0]['message']["content"]
            input_string = gpt_result
            test_passed, fatal_error = extract_and_run(input_string, raw_file_name, class_name, method_id, test_num,
                                                       project_name,
                                                       package)

            if test_passed:
                print(progress, Fore.GREEN + method_id, "test_" + str(test_num), "steps", steps, "rounds", rounds,
                      "test passed",
                      Style.RESET_ALL)
                break

            if not os.path.exists(raw_file_name):
                print(progress, Fore.RED + method_id, "test_" + str(test_num), "steps", steps, "rounds", rounds,
                      "no code in raw result", Style.RESET_ALL)
                break

            # Open up the raw result
            with open(get_latest_file(save_dir), "r") as f:
                raw_result = json.load(f)

            # 4. Start imports Repair
            steps += 1
            # print(progress, method_id, "test_" + str(test_num), "Fixing imports", "rounds", rounds)
            imports_file_name = os.path.join(save_dir, str(steps) + "_imports_" + str(rounds) + ".json")
            # run imports repair
            source_code = raw_result["source_code"]
            source_code = repair_imports(source_code, imports)
            test_passed, fatal_error = extract_and_run(source_code, imports_file_name, class_name, method_id, test_num,
                                                       project_name,
                                                       package)
            if test_passed:
                print(progress, Fore.GREEN + method_id, "test_" + str(test_num), "steps", steps, "rounds", rounds,
                      "test passed",
                      Style.RESET_ALL)
                break
            if fatal_error:
                print(progress, Fore.RED + method_id, "test_" + str(test_num), "steps", steps, "rounds", rounds,
                      "fatal error",
                      Style.RESET_ALL)
                break

            print(progress, Fore.YELLOW + method_id, "test_" + str(test_num), "Test failed, fixing...", "rounds",
                  rounds,
                  Style.RESET_ALL)
            if not repair:  # If we do not want to repair the code, we don't need to second round
                break
    except Exception as e:
        print(progress, Fore.RED + str(e), Style.RESET_ALL)
    if os.path.exists(run_temp_dir):
        run_temp_dir = os.path.abspath(run_temp_dir)
        shutil.rmtree(run_temp_dir)

def start_whole_process_02(source_dir, result_path, multiprocess=False, repair=True):
    """
    Start repair process
    :param repair:  Whether to repair the code
    :param multiprocess: Whether to use multiprocess
    :param source_dir: The directory of the dataset or scoped dataset.
    :return:
    """
    # Get a list of all file paths
    file_paths = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".json"):
                file_paths.append(os.path.join(root, file))

    submits = 0
    total = len(file_paths) * test_number
    if multiprocess:
        print("Multi process executing!")
        # Create a process pool with maximum of process_number
        with concurrent.futures.ProcessPoolExecutor(max_workers=process_number) as executor:
            for idx, file_path in enumerate(file_paths):
                _, base_name = os.path.split(file_path.replace("/dataset/", "/result/"))
                base_dir = os.path.join(result_path, base_name.split(".json")[0])
                for test_num in range(1, test_number + 1):
                    submits += 1
                    executor.submit(whole_process, test_num, base_name, base_dir, repair, submits, total)
        print("Main process executing!")
    else:
        print("Single process executing!")
        for idx, file_path in enumerate(file_paths):
            # print(Fore.YELLOW + "ID: " + str(idx), "filePath: ", file_path,Style.RESET_ALL)
            
            _, base_name = os.path.split(file_path.replace("/dataset/", "/result/"))
            base_dir = os.path.join(result_path, base_name.split(".json")[0])
            for test_num in range(1, test_number + 1):
                submits += 1
                whole_process(test_num, base_name, base_dir, repair, submits, total)
                break
            break


def start_whole_process(source_dir, result_path, multiprocess=False, repair=True):
    """
    Start repair process
    :param repair:  Whether to repair the code
    :param multiprocess: Whether to use multiprocess
    :param source_dir: The directory of the dataset or scoped dataset.
    :return:
    """
    # Get a list of all file paths
    file_paths = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".json"):
                file_paths.append(os.path.join(root, file))

    submits = 0
    total = len(file_paths) * test_number
    if multiprocess:
        print("Multi process executing!")
        # Create a process pool with maximum of process_number
        with concurrent.futures.ProcessPoolExecutor(max_workers=process_number) as executor:
            for idx, file_path in enumerate(file_paths):
                _, base_name = os.path.split(file_path.replace("/dataset/", "/result/"))
                base_dir = os.path.join(result_path, base_name.split(".json")[0])
                for test_num in range(1, test_number + 1):
                    submits += 1
                    executor.submit(whole_process, test_num, base_name, base_dir, repair, submits, total)
        print("Main process executing!")
    else:
        print("Single process executing!")
        for idx, file_path in enumerate(file_paths):
            # print(Fore.YELLOW + "ID: " + str(idx), "filePath: ", file_path,Style.RESET_ALL)
            
            _, base_name = os.path.split(file_path.replace("/dataset/", "/result/"))
            base_dir = os.path.join(result_path, base_name.split(".json")[0])
            for test_num in range(1, test_number + 1):
                submits += 1
                whole_process(test_num, base_name, base_dir, repair, submits, total)
                break
            break
