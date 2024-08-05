import os
import sys


def load_env(env_name):
    """ Load env variable and check its validity """
    env = os.getenv(env_name)
    # Check if env variables are set and if PACS_PORT is int
    if env is None:
        print(f"Error: Environment variable {env_name} not set.")
        sys.exit(1)
    elif env_name == 'PACS_PORT':
        try:
            env = int(env)
        except ValueError:
            print("Error: PACS_PORT environment variable is not a valid integer.")
            sys.exit(1)
    return env
