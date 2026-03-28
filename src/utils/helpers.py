from dotenv import load_dotenv
import os

load_dotenv()

def get_env(var_name, default=None):
    value = os.getenv(var_name, default)
    return value

def is_running_in_github_actions():
    return os.getenv('GITHUB_ACTIONS', 'false').lower() == 'true'
