import os
import qpfas
import argparse
from dask.distributed import get_task_stream 

parser = argparse.ArgumentParser()
parser.add_argument('-loc', type=str, required=True,
                    help="Location of where the code is executed. Either 'local' or the path of scheduler")
parser.add_argument('-yml', type=str, required=True, help="Path to yaml input file.")
parser.add_argument('-save_to', type=str, help="Name of saved file. If None, output is not saved.")
args = parser.parse_args()

if args.loc == 'local':
    client = qpfas.workflow.DaskDAG.create_client(dask_scheduler_uri="tcp://dask-scheduler:8786")

else:
    client = qpfas.workflow.DaskDAG.create_client(scheduler_file=args.loc)

print(f"Client: {client}")

YAML_FILE = os.path.join(os.getcwd(), args.yml)
graph, keys_to_gather, exp_params, dag_nodes = qpfas.workflow.EfficientDAG.load_from_yaml(YAML_FILE)


print(f"\nNumber of Experiments: {len(exp_params)}\nDAG Nodes:")
for i in dag_nodes:
    print(f"{i}: {dag_nodes[i]}")

print(f"\nKeys Gathered: {keys_to_gather}")

metadata = qpfas.utils.get_all_metadata()

global_start_timestamp = qpfas.utils.get_datetime_now()
with get_task_stream() as ts:  # necessary for timing logs
    results = qpfas.workflow.DaskDAG.get(client, graph, keys_to_gather)
global_end_timestamp = qpfas.utils.get_datetime_now()

metadata['global_start_timestamp'] = global_start_timestamp
metadata['global_end_timestamp'] = global_end_timestamp

results = qpfas.workflow.EfficientDAG.get_timing_logs(ts, exp_params, results, metadata)

if args.save_to:
    qpfas.workflow.EfficientDAG.write_to_file(args.save_to, exp_params, results)
