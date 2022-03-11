import os
import subprocess
import socket
import getpass
import uuid
import datetime
import ast
import json

# execute command in the shell
def execute_shell_command(shell_command: list) -> str:
    try:
        res = subprocess.run(shell_command, capture_output=True)
    except OSError:
        print(f'Error while executing command: {" ".join(shell_command)}')
        return None

    if res.returncode == 0:
        return res.stdout
    else:
        print(f'Command returned with non-zero exit code: {res.returncode}')
        return None

def get_hostname() -> str:
    return str(socket.getfqdn())

# device_id
def get_device_id() -> str:
    device_id = os.getenv('QPFAS_DEVICE_ID')
    if device_id is not None:
        return str(device_id)
    return get_hostname()

# toolchain
def get_conda_packages_list() -> str:
    conda_list_commmand = ['conda', 'list', '--json']

    conda_list = execute_shell_command(conda_list_commmand)

    if conda_list is not None:
        conda_list_json = json.dumps(ast.literal_eval(conda_list.decode('utf8')), indent=4, sort_keys=True)
        return conda_list_json

    return None

# user_id
def get_username() -> str:
    return str(getpass.getuser())

# group_id, experiment_id
def get_uuid() -> str:
    return str(uuid.uuid4())

# group_timestamp, experiment_timestamp_start, experiment_timestamp_end
def get_datetime_now() -> str:
    return str(datetime.datetime.now())

# qpfas_version OR repo tag OR repo SHA
def get_qpfas_version() -> str:
    # QPFAS VERSION
    try:
        import qpfas
        return str(qpfas.__version__)
    except (ImportError, ModuleNotFoundError, AttributeError) as e:
        pass

    # GIT TAG
    git_tag_commmand = ['git', 'describe']
    git_tag = execute_shell_command(git_tag_commmand)
    if git_tag is not None:
        return git_tag.decode('utf8').strip()

    # GIT SHA
    git_sha_commmand = ['git', 'rev-parse', 'HEAD']
    git_sha = execute_shell_command(git_sha_commmand)
    if git_sha is not None:
        return git_sha.decode('utf8').strip()

    return None

def get_all_metadata() -> dict:
    metadata = {}

    metadata['group_id'] = get_uuid()
    metadata['user_id'] = get_username()
    metadata['device_id'] = get_device_id()
    metadata['qpfas_version'] = get_qpfas_version()
    #metadata['toolchain'] = get_conda_packages_list()

    return metadata
