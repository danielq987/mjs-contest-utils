from dotenv import load_dotenv
import os

load_dotenv()

def get_env(var_name, default=None):
    value = os.getenv(var_name, default)
    return value
