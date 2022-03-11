import dask
import json
from dask.distributed import Client
from typing import Dict, List
from collections import ChainMap
from qpfas.workflow import Experiment


def gather_func(*argv):
    return [arg for arg in argv]


class DaskDAG:
    @staticmethod
    def create_client(processes: bool = False,
                      num_threads: int = 1,
                      num_workers: int = 1,
                      scheduler_file: str = None,
                      dask_scheduler_uri: str = None):
        if scheduler_file is not None:
            client = Client(scheduler_file=scheduler_file)
        elif dask_scheduler_uri is not None:
            client = Client(dask_scheduler_uri)
        else:
            client = Client(threads_per_worker=num_threads, n_workers=num_workers)
        return client

    @staticmethod
    def merge_dag_exp_list(exp_list: List[Experiment]):
        """ Merge individual DAGs to larger DAG. """
        return dict(ChainMap(*[exp.dag for exp in exp_list]))

    @staticmethod
    def merge_dag_list(dag_list: List[dict]):
        """ Merge individual DAGs to larger DAG. """
        return dict(ChainMap(*[dag for dag in dag_list]))

    @staticmethod
    def get(client: dask.distributed.Client, dag: Dict, return_key: str):
        if client is not None:
            return client.get(dag, return_key)
        return None

    @staticmethod
    def add_dag_nodes(dag: Dict, nodes: Dict):
        return {**dag, **nodes}

    @staticmethod
    def add_dag_node(dag: Dict, func, arg_list: List, return_key: str):
        return {**dag, return_key: (func, *arg_list)}

    @staticmethod
    def add_gather_node(dag: Dict, keys: List[str], return_key: str = 'gather'):
        return {**dag, return_key: (gather_func, *keys)}

    @staticmethod
    def visualize_dag(dag: dict, filename_svg: str = None):
        if filename_svg is not None:
            return dask.visualize(dag, filename=filename_svg)
        else:
            return dask.visualize(dag)

    @staticmethod
    def write_to_file(path, experiment_inputs, experiment_outputs, benchmarks):
        vqe_exp_data = [{**i, **j} for i, j in zip(experiment_inputs, experiment_outputs)]
        for i in vqe_exp_data:
            for j in benchmarks.keys():
                i[j] = benchmarks[j]

        with open(path + '.json', 'w') as fout:
            json.dump(vqe_exp_data, fout, indent=4)

    @staticmethod
    def get_timing_logs(merged_dags, task_stream, exp_params_list, results):
        for key in merged_dags:
            task_output = next((x for x in task_stream.data if x['key'] == key), None)
            if (task_output is not None) and (task_output['key'] != 'benchmark_energies'):
                compute_timing = next((x for x in task_output['startstops'] if x['action'] == 'compute'), None)
                uid = int(key.split('-')[-1])
                results_index = exp_params_list.index(next((x for x in exp_params_list if x['uid'] == uid), None))

                if 'tasks' not in results[results_index]:
                    results[results_index]['tasks'] = []

                results[results_index]['tasks'].append({'task': key,
                                                        'start': compute_timing['start'],
                                                        'stop': compute_timing['stop'],
                                                        'duration': compute_timing['stop'] - compute_timing['start']})
        return results
