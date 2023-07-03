import numpy as np
import os
from importlib import import_module
from tqdm import tqdm


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
    settings_filename = "settings.npy"
    settings_fp = os.path.join(dataset_folder, settings_filename)
    settings = np.load(settings_fp)

    crn_module = import_module(model_name)
    crn_class = getattr(crn_module, model_name)
    crn_instance = crn_class(endtime, timestep)

    param_settings = []
    if params_to_randomize is not None:
        randomized = crn_instance.get_randomized_parameters(
            params_to_randomize, nb_settings, 0.2
        )
        for i in range(nb_settings):
            d = {}
            for key in randomized:
                d[key] = randomized[key][i]
            param_settings.append(d)

    if param_settings:
        kwargs = [(settings[n], n, param_settings[n]) for n in range(nb_settings)]
    else:
        kwargs = [(settings[n], n, None) for n in range(nb_settings)]

    for arg in kwargs:
        _single_simulation(
            *arg,
            model_name=model_name,
            crn_instance=crn_instance,
            nb_trajectories=nb_trajectories,
            dataset_folder=dataset_folder,
            prefix=prefix,
        )

    if how == "concat":
        dataset = _concatenate_simulations(nb_settings, dataset_folder, prefix=prefix)
    elif how == "stack":
        dataset = _stack_simulations(nb_settings, dataset_folder, prefix=prefix)
    else:
        raise ValueError("'how' accepts only two arguments: 'concat' and 'stack'.")

    return dataset


def _concatenate_simulations(nb_settings, dataset_folder, prefix="partial_"):
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
        os.remove(partial_dataset_filepath)
    return final_dataset


def _stack_simulations(nb_settings, dataset_folder, prefix="partial_"):
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
    crn_instance.set_species_initial_value(initial_values)

    if params_dict is not None:
        crn_instance.set_parameters(params_dict)

    trajectories = crn_instance.run(number_of_trajectories=nb_trajectories)
    data = np.stack(trajectories.to_array())

    if params_dict is not None:
        vals = np.array(list(params_dict.values()))
        x = np.ones(list(data.shape[:-1]) + [1]) * vals
        data = np.concatenate([data, x], axis=-1)

    partial_dataset_filename = str(prefix) + str(id_number) + ".npy"
    partial_dataset_filepath = os.path.join(dataset_folder, partial_dataset_filename)
    np.save(partial_dataset_filepath, data)
