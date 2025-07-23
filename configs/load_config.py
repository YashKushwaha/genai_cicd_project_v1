import configparser
import os

config = configparser.ConfigParser()
config.read('configs/infra_config.ini')

# Write to GitHub environment file
github_env = os.environ.get('GITHUB_ENV', 'temp.txt')
print('github_env -> ', github_env)

with open(github_env, 'a') as env_file:
    for section in config.sections(): 
        for key, val in dict(config.items(section)).items():
            _ = f'{section}_{key}'.upper()
            print(_)
            env_file.write(f"{_}={val}\n")

print(f"Wrote to {github_env}:")
with open(github_env) as f:
    print(f.read())