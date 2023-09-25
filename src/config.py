import configparser

# Use configparser.ConfigParser() to read config.ini file.
config = configparser.ConfigParser()
config.read("../config/config.ini")

process_number = eval(config.get("DEFAULT", "process_number"))
test_number = eval(config.get("DEFAULT", "test_number"))
max_attempts = eval(config.get("DEFAULT", "max_attempts"))
MAX_PROMPT_TOKENS = eval(config.get("DEFAULT", "MAX_PROMPT_TOKENS"))
MIN_ERROR_TOKENS = eval(config.get("DEFAULT", "MIN_ERROR_TOKENS"))
TIMEOUT = eval(config.get("DEFAULT", "TIMEOUT"))

TEMPLATE_BASIC = config.get("DEFAULT", "PROMPT_TEMPLATE_BASIC")
TEMPLATE_WITH_DEV_COMMENTS = config.get("DEFAULT", "PROMPT_TEMPLATE_WITH_DEV_COMMENTS")
TEMPLATE_NO_DEPS = config.get("DEFAULT", "PROMPT_TEMPLATE_NO_DEPS")
TEMPLATE_WITH_DEPS = config.get("DEFAULT", "PROMPT_TEMPLATE_DEPS")
TEMPLATE_ERROR = config.get("DEFAULT", "PROMPT_TEMPLATE_ERROR")

LANGUAGE = config.get("DEFAULT", "LANGUAGE")
GRAMMAR_FILE = config.get("DEFAULT", "GRAMMAR_FILE")
COBERTURA_DIR = config.get("DEFAULT", "COBERTURA_DIR")
JUNIT_JAR = config.get("DEFAULT", "JUNIT_JAR")
MOCKITO_JAR = config.get("DEFAULT", "MOCKITO_JAR")
LOG4J_JAR = config.get("DEFAULT", "LOG4J_JAR")
JACOCO_AGENT = config.get("DEFAULT", "JACOCO_AGENT")
JACOCO_CLI = config.get("DEFAULT", "JACOCO_CLI")
REPORT_FORMAT = config.get("DEFAULT", "REPORT_FORMAT")

dataset_dir = config.get("DEFAULT", "dataset_dir")
result_dir = config.get("DEFAULT", "result_dir")
test_dir = config.get("DEFAULT", "test_dir")
db_file = config.get("DEFAULT", "db_file")
csv_entries_file = config.get("DEFAULT", "csv_entries_file")
final_result_file = config.get("DEFAULT", "final_result_file")

testsdb_file = config.get("DEFAULT", "testsdb_file")
default_project_dir = config.get("DEFAULT", "project_dir")
class_info_output = config.get("DEFAULT", "class_info_output")

api_keys = eval(config.get("openai", "api_keys"))
LLM_BASE_PATH = config.get("DEFAULT", "llm_base_path")

model = config.get("llm", "model")
temperature = eval(config.get("llm", "temperature"))
top_p = eval(config.get("llm", "top_p"))
frequency_penalty = eval(config.get("llm", "frequency_penalty"))
presence_penalty = eval(config.get("llm", "presence_penalty"))
n_predict = eval(config.get("llm", "n_predict"))
top_k = eval(config.get("llm", "top_k"))
n_batch = eval(config.get("llm", "n_batch"))
repeat_penalty = eval(config.get("llm", "repeat_penalty"))
repeat_last_n = eval(config.get("llm", "repeat_last_n"))
