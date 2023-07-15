from pathlib import Path
from time import time
import pickle
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np

from workflow_manager import WorkflowManager
from data_manager import DataManager

# initialisation
wf_manager = WorkflowManager()
wf_manager.init_data_manager(
    scrn_filepath="example.xml",
    n_initial_conditions=10000,
    n_simulations_per_condition=10,
)
wf_manager.init_deep_abstraction()

# simulation dataset generation/loading
if Path("sim_data.npy").exists():
    wf_manager.load_simulation_data()
else:
    wf_manager.generate_simulation_data()
    wf_manager.save_simulation_data()
wf_manager.prepare_data_loaders(batch_size=64)

# deep abstraction training/loading
# wf_manager.train_deep_abstraction(n_epochs=100, patience=10)
# wf_manager.validate_deep_abstraction()
wf_manager.load_deep_abstraction()


# comparison of Tellurium and Deep Abstraction
## speed of simulation
# n_init_conditions = [1, 10, 100, 200, 500, 1000, 1500]
# n_sims_per_init_condition = [1, 10, 100, 200, 500, 1000, 1500]
# results = {
#     "te": {"init_conditions": dict()},
#     "da": {"init_conditions": dict()},
# }

# for i in n_init_conditions:
#     results["te"]["init_conditions"][f"{i}"] = {"sims_per_condition": dict()}
#     results["da"]["init_conditions"][f"{i}"] = {"sims_per_condition": dict()}
#     for j in n_sims_per_init_condition:
#         # Tellurium
#         dm = DataManager(n_initial_conditions=i, n_simulations_per_condition=j)
#         start_te = time()
#         dm.simulate()
#         end_te = time() - start_te
#         print(
#             f">> Finished Te simulation for {i} init conditions and {j} sims per init condition"
#         )
#         results["te"]["init_conditions"][f"{i}"]["sims_per_condition"][f"{j}"] = end_te

#         start_da = time()
#         wf_manager.produce_chain_of_states(j)
#         end_da = time() - start_da
#         print(
#             f">> Finished DA simulation for {i} init conditions and {j} sims per init condition\n"
#         )
#         results["da"]["init_conditions"][f"{i}"]["sims_per_condition"][f"{j}"] = end_da

# with open("eval_results.pkl", "wb") as file:
#     pickle.dump(results, file)

# with open("eval_results.pkl", "rb") as file:
#     results = pickle.load(file)

# data = results

# x_ticks = list(map(int, data["te"]["init_conditions"].keys()))
# fig, axs = plt.subplots(2, figsize=(10, 14))

# for system in ["da", "te"]:
#     y_ticks = [
#         sum(data[system]["init_conditions"][str(x)]["sims_per_condition"].values())
#         / len(data[system]["init_conditions"][str(x)]["sims_per_condition"])
#         for x in x_ticks
#     ]
#     axs[0].plot(x_ticks, y_ticks, marker="o", label=system)
# axs[0].set_xlabel("Number of Initial Conditions")
# axs[0].set_ylabel("Average Simulation Time")
# axs[0].legend()
# axs[0].grid()
# axs[0].set_title("Average Simulation Time vs Number of Initial Conditions")

# for system in ["da", "te"]:
#     avg_times = []
#     for num_sims in x_ticks:
#         total_time = 0
#         count = 0
#         for num_init in x_ticks:
#             time = data[system]["init_conditions"][str(num_init)]["sims_per_condition"][
#                 str(num_sims)
#             ]
#             total_time += time
#             count += 1
#         avg_time = total_time / count
#         avg_times.append(avg_time)
#     axs[1].plot(x_ticks, avg_times, marker="o", label=system)

# axs[1].set_xlabel("Number of Simulations per Condition")
# axs[1].set_ylabel("Average Simulation Time")
# axs[1].legend()
# axs[1].grid()
# axs[1].set_title("Average Simulation Time vs Number of Simulations per Condition")

# plt.tight_layout()
# plt.show()

## accuracy of simulation
# results = {"init_conditions": dict()}
# dm = DataManager(n_initial_conditions=1000, n_simulations_per_condition=10)
# init_conditions = dm.init_concentrations
# randomized_parameters = dm.randomized_parameters
# params_dict = dm.get_randomized_params_dict()


# def compute_average(arr):
#     averages = np.mean(arr, axis=0)

#     return averages


# for i, init_condition in enumerate(init_conditions):
#     if i % 10 == 0:
#         print(f">> testing initial condition {i+1}/{dm.n_initial_conditions}")
#     results["init_conditions"][f"{i}"] = {"te": None, "da": None}

#     # te
#     te_res = dm.simulate_for_single_initial_condition(
#         init_condition, randomized_parameters[i]
#     )
#     te_res = compute_average(te_res)
#     results["init_conditions"][f"{i}"]["te"] = te_res

#     # da
#     init_condition_concentrations = (
#         wf_manager.data_manager.extract_species_concentrations_from_init_condition_dict(
#             init_condition
#         )
#     )
#     prepped_init_condition = wf_manager.prepare_initial_condition_for_input(
#         init_condition_concentrations, random_index=i, params_dict=params_dict
#     )
#     da_res = []
#     for j in range(dm.n_simulations_per_condition):
#         curr_res = wf_manager.produce_chain_of_states(
#             random_index=i, initial_state=prepped_init_condition
#         )
#         curr_res = wf_manager.convert_tensors_to_numpy(curr_res)
#         da_res.append(curr_res)
#     da_res = np.concatenate([np.expand_dims(a, axis=0) for a in da_res], axis=0)
#     da_res = compute_average(da_res)
#     results["init_conditions"][f"{i}"]["da"] = da_res

# with open("accuracy_results.pkl", "wb") as file:
#     pickle.dump(results, file)

# with open("accuracy_results.pkl", "rb") as file:
#     results = pickle.load(file)


# def rmse(actual, pred):
#     actual, pred = np.array(actual), np.array(pred)
#     return np.sqrt(np.square(np.subtract(actual, pred)).mean())


# def calculate_errors(nested_dict):
#     error_dict = {}
#     for condition, data in nested_dict.items():
#         error_dict[condition] = {}
#         for key in data:
#             error_dict[condition][key] = rmse(data[key]["da"], data[key]["te"])
#     return error_dict


# def average_error(error_dict):
#     total_error = 0
#     count = 0
#     for condition, errors in error_dict.items():
#         for error in errors.values():
#             total_error += error
#             count += 1
#     return total_error / count


# err = calculate_errors(results)
# avg_err = average_error(err)

# pprint(avg_err)


# for i in n_init_conditions:
#     results["te"]["init_conditions"][f"{i}"] = {"sims_per_condition": dict()}
#     results["da"]["init_conditions"][f"{i}"] = {"sims_per_condition": dict()}
#     for j in n_sims_per_init_condition:
#         # Tellurium
#         dm = DataManager(n_initial_conditions=i, n_simulations_per_condition=j)
#         start_te = time()
#         dm.simulate()
#         end_te = time() - start_te
#         print(
#             f">> Finished Te simulation for {i} init conditions and {j} sims per init condition"
#         )
#         results["te"]["init_conditions"][f"{i}"]["sims_per_condition"][f"{j}"] = end_te

#         start_da = time()
#         wf_manager.produce_chain_of_states(j)
#         end_da = time() - start_da
#         print(
#             f">> Finished DA simulation for {i} init conditions and {j} sims per init condition\n"
#         )
#         results["da"]["init_conditions"][f"{i}"]["sims_per_condition"][f"{j}"] = end_da
