import logging
import multiprocessing
import numpy as np
import os

from functools import partial
from importlib import import_module
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.colors as colours
from time import time

from pprint import pprint
from pathlib import Path
import random

LOGGER = logging.getLogger("dataset.simulation")


def build_simulation_dataset(
    model_name,
    nb_settings,
    nb_trajectories,
    timestep,
    endtime,
    dataset_folder,
    params_to_randomize=None,
    prefix="partial_",
    how="concat",
    **kwargs,
):
    """
    Produce dataset of simulations.
    Runs Gillespie simulations of selected model w.r.t given
    parameters (discrete time-step, number of initial settings,
    and number of simulations for each of the initial settings).
    Depending on `how` parameter, simulated trajectories are gathered
    in particularly shaped multi-dimensional array.

    Parameters
    ----------
    model_name : string name of CRN model class.
        *Note*: file containing model class is assumed to have
        the same name (e.g. 'EGFR.py' and 'class EFGR').
    nb_settings : number of initial states for simulations.
        Initial states are (randomly) produced by CRN model class.
    nb_trajectories : number of trajectories to simulate starting from each of the initial states.
    timestep : discrete time-step for simulations.
    endtime : end-time for simulations.
    dataset_folder : folder to store results and related data, such as initial settings.
    params_to_randomize : list of string names of model parameters to randomize.
    prefix : string prefix for temporary files.
    how : string, one of {'concat', 'stack'}. Defines final shape of returned dataset.
        'concat' is used for training dataset;
        'stack' - for histogram dataset, so that we can easily build histograms for different initial settings

    Returns
    -------
    dataset : np.array
     of shape (nb_settings * nb_trajectories, number-of-steps, number-of-species) If `how` == 'concat'
     or       (nb_settings, nb_trajectories, number-of-steps, number-of-species) If `how` == 'stack'

    """
    _perform_simulations(
        model_name,
        nb_settings,
        nb_trajectories,
        timestep,
        endtime,
        dataset_folder,
        params_to_randomize=params_to_randomize,
        prefix=prefix,
        **kwargs,
    )
    if how == "concat":
        LOGGER.info(">>>> starting concatenate_simulations...")
        dataset = _concatenate_simulations(nb_settings, dataset_folder, prefix=prefix)
        LOGGER.info(">>>> done...")
    elif how == "stack":
        LOGGER.info(">>>> starting stack_simulations...")
        dataset = _stack_simulations(nb_settings, dataset_folder, prefix=prefix)
        LOGGER.info(">>>> done...")
    else:
        raise ValueError("'how' accepts only two arguments: " "'concat' and 'stack'.")
    return dataset


def _concatenate_simulations(nb_settings, dataset_folder, prefix="partial_"):
    """Read temporary files from folder and concatenate containing data."""
    for i in tqdm(range(nb_settings)):
        partial_dataset_filename = str(prefix) + str(i) + ".npy"
        partial_dataset_filepath = os.path.join(
            dataset_folder, partial_dataset_filename
        )
        with open(partial_dataset_filepath, "rb") as f:
            partial_dataset = np.load(f)
        if i == 0:
            final_dataset = partial_dataset
        else:
            final_dataset = np.vstack([final_dataset, partial_dataset])
            # final_dataset = np.concatenate(
            #     (final_dataset, partial_dataset),
            #     axis=0,
            # )
        os.remove(partial_dataset_filepath)
    return final_dataset


def _stack_simulations(nb_settings, dataset_folder, prefix="partial_"):
    """Read temporary files from folder and stack containing data."""
    for i in tqdm(range(nb_settings)):
        partial_dataset_filename = str(prefix) + str(i) + ".npy"
        partial_dataset_filepath = os.path.join(
            dataset_folder, partial_dataset_filename
        )
        with open(partial_dataset_filepath, "rb") as f:
            partial_dataset = np.load(f)
        if i == 0:
            final_dataset = partial_dataset[np.newaxis, ...]
        else:
            final_dataset = np.concatenate(
                (final_dataset, partial_dataset[np.newaxis, ...]),
                axis=0,
            )
        os.remove(partial_dataset_filepath)
    return final_dataset


def _perform_simulations(
    model_name,
    nb_settings,
    nb_trajectories,
    timestep,
    endtime,
    dataset_folder,
    params_to_randomize,
    prefix="partial_",
    settings_filename="settings.npy",
):
    """Perform simulations, save intermediate results and initial settings to `dataset_folder`."""
    settings_fp = os.path.join(dataset_folder, settings_filename)
    settings = np.load(settings_fp)

    crn_module = import_module(model_name)
    crn_class = getattr(crn_module, model_name)
    crn_instance = crn_class(endtime, timestep)

    param_settings = []
    if params_to_randomize is not None:
        randomized = crn_instance.get_randomized_parameters(
            params_to_randomize, nb_settings
        )
        for i in range(nb_settings):
            d = {}
            for key in randomized:
                d[key] = randomized[key][i]
            param_settings.append(d)

    count = (multiprocessing.cpu_count() // 3) * 2 + 1
    LOGGER.info(" ===== CPU Cores used for simulations: %s =====" % count)
    pool = multiprocessing.Pool(processes=count)

    if param_settings:
        kwargs = [(settings[n], n, param_settings[n]) for n in range(nb_settings)]
    else:
        kwargs = [(settings[n], n, None) for n in range(nb_settings)]

    task = partial(
        _single_simulation,
        model_name=model_name,
        crn_instance=crn_instance,
        nb_trajectories=nb_trajectories,
        dataset_folder=dataset_folder,
        prefix=prefix,
    )

    pool.starmap(task, kwargs)
    pool.close()
    return


def _single_simulation(
    initial_values,
    id_number,
    params_dict,
    model_name,
    crn_instance,
    nb_trajectories,
    dataset_folder,
    prefix,
):
    """Helper single-thread function."""
    crn_instance.set_species_initial_value(initial_values)

    if params_dict is not None:
        crn_instance.set_parameters(params_dict)

    trajectories = crn_instance.run(
        number_of_trajectories=nb_trajectories
        # show_labels=False
    )

    species_names = crn_instance.get_species_names()
    trajectory = trajectories[0]
    if model_name != "BD20":
        list_of_colours = [
            x for x in colours.ColorConverter.colors.keys() if len(x) < 3
        ] * 10
    else:
        list_of_colours = [
            "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])
            for i in range(20)
        ]
    fname = str(time()).split(".")[0][6:]
    for i, name in enumerate(species_names):
        plt.plot(trajectory["time"], trajectory[name], list_of_colours[i], label=name)
    plt.legend()
    plt.title(f"{model_name}, {len(trajectories)} trajectories")
    plt.savefig(rf"{model_name}\{crn_instance.get_n_species()}_species_{fname}.png")
    plt.close()

    data = trajectories.to_array()  # produces a list of nb_trajectories arrays
    # print(f'\nprinting trajectory: {data[0][0]}')
    data = np.stack(data)  # stacks the arrays from the above list into a new dimension
    # data = np.vstack(data) # stacks the arrays vertically, dim: (nb_trajectories * steps, nb_species)

    if params_dict is not None:
        vals = np.array(list(params_dict.values()))
        x = np.ones(list(data.shape[:-1]) + [1]) * vals
        data = np.concatenate([data, x], axis=-1)

    _save_simulation_data(data, dataset_folder, prefix, id_number)


def _save_simulation_data(
    data,
    dataset_folder,
    prefix,
    id_number,
):
    """Save data to `dataset_folder` using `id_number` and `prefix` for the filename."""
    partial_dataset_filename = str(prefix) + str(id_number) + ".npy"
    partial_dataset_filepath = os.path.join(dataset_folder, partial_dataset_filename)
    LOGGER.info(f"Saving to partial_dataset_filepath: {partial_dataset_filepath}")
    np.save(partial_dataset_filepath, data)
    LOGGER.info("Saved.")
    return
