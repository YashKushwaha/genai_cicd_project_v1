import configparser
import os

config = configparser.ConfigParser()
config.read('infra_config.ini')



# Write to GitHub environment file
github_env = os.environ.get('GITHUB_ENV', 'temp.txt')
with open(github_env, 'w') as env_file:
    for section in config.sections(): 
        for key, val in dict(config.items(section)).items():
            _ = f'{section}_{key}'.upper()
            env_file.write(f"{_}={val}\n")

