import yaml
import json
from datetime import datetime
from qpfas.workflow.wrapper import *
from os import listdir
from itertools import product


def cart_prod_dict(x):
    """ Given a dictionary x, returns a list of all dictionaries formed by cartesian product """
    vals = [x[i] if type(x[i]) == list else [x[i]] for i in x.keys()]
    return [dict(zip(x.keys(), i)) for i in list(product(*vals))]


def argument_set_new(arg_i, arg_history):
    """
    If the arguments in arg_i are not contained in arg_history -1 is returned in indicating a new branch,
    otherwise the branch number is returned
    """
    if len(arg_history) == 0:
        return -1
    else:
        for c, arg_set in enumerate(arg_history):
            if arg_i == arg_set:
                return c
        return -1


class EfficientDAG:
    """
    Class for creating an efficient DAG (no duplicate calculations) from a YAML file
    """
    @staticmethod
    def create_efficient_dag(experiment_dict: dict):
        experiment_dict["time_stamp"] = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        # check if all molecules in directory
        if experiment_dict["molecule"] == "all_in_path":
            experiment_dict["molecule"] = EfficientDAG.get_all_molecules_in_path(experiment_dict["molecule_path"])

        # create distortians if necessary
        if "distortion_dict" in experiment_dict.keys():
            distortion_dict = experiment_dict["distortion_dict"]
            bond_distances = qpfas.chemistry.create_distortions(distortion_dict["equilibrium_geom"],
                                                                distortion_dict["atom_bond_indices"],
                                                                distortion_dict["stretch_params"],
                                                                experiment_dict["molecule_path"],
                                                                experiment_dict["molecule"])
            experiment_dict["mol_dist_id"] = list(range(len(bond_distances)))
            experiment_dict["bond_distortion"] = True
        else:
            experiment_dict["bond_distortion"] = False

        # get benchmarks and convert to list if needed
        benchmark_cond = False
        if ("benchmark" in experiment_dict.keys()) and ("benchmark_solver" in experiment_dict.keys()):
            if type(experiment_dict["benchmark"]) != list:
                experiment_dict["benchmark"] = [experiment_dict["benchmark"]]
            benchmark_energies = experiment_dict["benchmark"]
            del experiment_dict["benchmark"]
            benchmark_cond = True

        # get stages of the experiment
        stages = experiment_dict["stages"]
        del experiment_dict["stages"]

        # get the experiment parameters & add ids to the experiments
        exp_params = cart_prod_dict(experiment_dict)
        n_exp = len(exp_params)
        for i in range(n_exp):
            exp_params[i]["uid"] = i

        if "distortion_dict" in experiment_dict.keys():
            for i in range(n_exp):
                exp_params[i]["bond_distance"] = bond_distances[exp_params[i]["mol_dist_id"]]

        # create dag
        arg_branch = [[] for _ in stages]
        ret_branch = [{} for _ in exp_params]
        graph = {}

        for exp_count in range(n_exp):
            for node_count, node in enumerate(stages):
                # get arguments
                args = []
                for node_arg in node['args']:
                    # check if argument is in the experiment parameters
                    if node_arg in exp_params[exp_count].keys():
                        args.append(exp_params[exp_count][node_arg])

                    # check if argument has been returned by a function earlier in the graph
                    elif node_arg in ret_branch[exp_count].keys():
                        args.append(f"{node_arg}-{ret_branch[exp_count][node_arg]}")

                # check if a new set of arguments (in which case branch_num==-1)
                branch_num = argument_set_new(args, arg_branch[node_count])
                if branch_num == -1:
                    branch_num = len(arg_branch[node_count])
                    arg_branch[node_count].append(args)

                    # add to graph
                    graph[f"{node['ret']}-{branch_num}"] = (eval(node['func']), *args)

                ret_branch[exp_count][node['ret']] = branch_num
            exp_params[exp_count]["node_history"] = ret_branch[exp_count]

        # get number of nodes per stage
        dag_nodes = [len(i) for i in arg_branch]
        dag_nodes = {i["ret"]: j for i, j in zip(stages, dag_nodes)}

        # get keys (the keys are the end nodes)
        keys_to_gather = [f"{list(dag_nodes.keys())[-1]}-{i}" for i in range(n_exp)]

        # add benchmarks
        if benchmark_cond:
            dag_nodes["benchmark_energies"] = dag_nodes["molecule_tq"]
            for i in range(dag_nodes["benchmark_energies"]):
                if experiment_dict["benchmark_solver"] == "psi4":
                    graph[f"benchmark_energies-{i}"] = (compute_benchmark_energies, f"molecule_tq-{i}", benchmark_energies)
                elif experiment_dict["benchmark_solver"] == "pyscf":
                    graph[f"benchmark_energies-{i}"] = (compute_benchmark_energies_pyscf, f"molecule_qpfas-{i}", benchmark_energies)
            keys_to_gather += [f"benchmark_energies-{i}" for i in range(dag_nodes["benchmark_energies"])]

        return graph, keys_to_gather, exp_params, dag_nodes

    @staticmethod
    def load_from_yaml(filename: str):
        with open(filename, 'r') as f:
            experiment_dict = list(yaml.load_all(f, Loader=yaml.FullLoader))[0]
            return EfficientDAG.create_efficient_dag(experiment_dict)

    @staticmethod
    def get_all_molecules_in_path(path):
        return [i.split(".")[0] for i in listdir(path) if '.xyz' in i]

    @staticmethod
    def write_to_file(path, exp_params, exp_outputs):
        n_exp = len(exp_params)

        # convert ansatz from a list into two columns
        for i in exp_params:
            if "ansatz" in i:
                i["ansatz_name"], i["ansatz_depth"] = i["ansatz"]
                del i["ansatz"]

        vqe_exp_data = [{**exp_params[i], **exp_outputs[i]} for i in range(n_exp)]

        # add in benchmark data (if any)
        if len(exp_outputs) > n_exp:
            benchmark_results = exp_outputs[n_exp:]
            for i in vqe_exp_data:
                benchmark_id = i["node_history"]["molecule_tq"]
                for j in benchmark_results[benchmark_id].keys():
                    i[j] = benchmark_results[benchmark_id][j]

        with open(path + '.json', 'w') as fout:
            json.dump(vqe_exp_data, fout, indent=4)

    @staticmethod
    def get_timing_logs(task_stream, exp_params, results, metadata):
        n_exp = len(exp_params)

        for uid in range(n_exp):
            results[uid]['timings_dask'] = {}
            results[uid]['nbytes_dask'] = {}
            results[uid]['worker_dask'] = {}
            results[uid]['experiment_id'] = metadata['group_id'] + '_' + str(uid)
            for key, value in metadata.items():
                results[uid][key] = value

        for i in task_stream.data:
            time_data = {}
            for exec_time in i['startstops']:
                time_data[exec_time['action']] = {"start": exec_time['start'],
                                                  "stop": exec_time['stop'],
                                                  "duration": exec_time['stop'] - exec_time['start']}
            if "benchmark_energies" not in i['key']:
                node_name, node_index = i['key'].split('-')
                for uid in range(n_exp):
                    if exp_params[uid]["node_history"][node_name] == int(node_index):
                        results[uid]['timings_dask'][i['key']] = time_data
                        results[uid]['nbytes_dask'][i['key']] = i['nbytes']
                        results[uid]['worker_dask'][i['key']] = i['worker']
            else:
                _, node_index = i['key'].split('-')
                for uid in range(n_exp):
                    if exp_params[uid]["node_history"]["molecule_tq"] == int(node_index):
                        results[uid]['timings_dask'][i['key']] = time_data
                        results[uid]['nbytes_dask'][i['key']] = i['nbytes']
                        results[uid]['worker_dask'][i['key']] = i['worker']

        return results


def reconstruct_graph(node_history):
    """
    This is a function to reconstruct the dask graph from the node history results
    """
    graph = {}
    for i in node_history:
        # add starting molecule data to graph
        if f"molecule_qpfas-{i['molecule_qpfas']}" not in graph:
            graph[f"molecule_qpfas-{i['molecule_qpfas']}"] = (eval("place_holder"),)

        if f"molecule_tq-{i['molecule_tq']}" not in graph:
            graph[f"molecule_tq-{i['molecule_tq']}"] = (
            eval("place_holder"), f"molecule_qpfas-{i['molecule_qpfas']}")
            graph[f"qubit_hamiltonian_tq-{i['molecule_tq']}"] = (eval("place_holder"), f"molecule_tq-{i['molecule_tq']}")
            graph[f"benchmark_energies-{i['molecule_tq']}"] = (eval("place_holder"), f"molecule_tq-{i['molecule_tq']}")

        graph[f"vqe_output-{i['vqe_output']}"] = (
        eval("place_holder"), f"molecule_tq-{i['molecule_tq']}", f"qubit_hamiltonian_tq-{i['qubit_hamiltonian_tq']}")
        graph[f"vqe_results-{i['vqe_results']}"] = (eval("place_holder"), f"vqe_output-{i['vqe_output']}")
        graph[f"vqe_ansatz-{i['vqe_ansatz']}"] = (eval("place_holder"), f"vqe_output-{i['vqe_output']}")
        graph[f"gate_stats-{i['gate_stats']}"] = (eval("place_holder"), f"vqe_ansatz-{i['vqe_ansatz']}")
        graph[f"results-{i['results']}"] = (
        eval("place_holder"), f"vqe_results-{i['vqe_results']}",
        f"molecule_qpfas-{i['molecule_qpfas']}", f"gate_stats-{i['gate_stats']}")
    return graph


def place_holder(*args):
    # function for graph reconstruction
    ...
