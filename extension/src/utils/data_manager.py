import tellurium as te
import numpy as np

import torch
from torch.utils.data import Dataset


class DataWrapper(Dataset):
    """
    Used for wrapping raw NumPy data. Training and testing sets should be wrapped separately.
    """

    def __init__(self, data):
        self.data = data

    def __getitem__(self, index):
        """
        Inputs contain all information: time, species concentrations, reaction rates.
        Targets only contain species concentrations.
        """
        species_concentration_indices = [1, 2, 3]

        inputs = self.data[index, :-1, :].astype(np.float32)
        targets = self.data[index, 1:, species_concentration_indices].astype(np.float32)
        targets = np.transpose(targets, (1, 0))

        return (torch.from_numpy(inputs), torch.from_numpy(targets))

    def __len__(self):
        return len(self.data)


class DataManager:
    """
    General class for interfacing with Tellurium-based simulation and model handling.
    """

    def __init__(
        self,
        definition,
        n_initial_conditions=10,
        n_simulations_per_condition=10,
        steps=10,
        endtime=1.0,
        random_seed=np.random.randint(0, 1_000_000_000),
    ):
        self.definition = definition
        self.n_initial_conditions = n_initial_conditions
        self.n_simulations_per_condition = n_simulations_per_condition
        self.steps = steps
        self.endtime = endtime
        self.random_seed = random_seed

        self.model = self.set_up_model()
        self.init_concentrations = self.randomize_species_concentrations()
        self.randomized_parameters = self.randomize_parameters()

    def simulate(self):
        results = []

        for init_condition in range(self.n_initial_conditions):
            if init_condition % 50 == 0:
                print(
                    f"perfoming stochastic simulation for initial condition {init_condition+1}/{self.n_initial_conditions}..."
                )
            for sim_iteration in range(self.n_simulations_per_condition):
                self.model.reset()
                self.assign_custom_values_to_model(
                    self.init_concentrations[init_condition]
                )
                self.assign_custom_values_to_model(
                    self.randomized_parameters[init_condition]
                )
                sim = self.model.simulate(0.0, self.endtime, self.steps + 1)

                # Add the randomized parameters as new columns
                for param_name, param_value in self.randomized_parameters[
                    init_condition
                ].items():
                    param_column = np.full((sim.shape[0], 1), param_value)
                    sim = np.hstack((sim, param_column))

                results.append(sim)

        return np.concatenate([np.expand_dims(a, axis=0) for a in results], axis=0)

    def simulate_for_single_initial_condition(
        self, init_condition, randomized_parameters
    ):
        results = []
        for sim_iteration in range(self.n_simulations_per_condition):
            self.model.reset()
            self.assign_custom_values_to_model(init_condition)
            self.assign_custom_values_to_model(randomized_parameters)
            sim = self.model.simulate(0.0, self.endtime, self.steps + 1)

            # Add the randomized parameters as new columns
            for param_name, param_value in randomized_parameters.items():
                param_column = np.full((sim.shape[0], 1), param_value)
                sim = np.hstack((sim, param_column))

            results.append(sim)
        return np.concatenate([np.expand_dims(a, axis=0) for a in results], axis=0)

    def set_up_model(self):
        model = te.loada(self.definition)
        model.integrator = "gillespie"
        model.integrator.seed = self.random_seed

        return model

    import numpy as np

    def randomize_species_concentrations(self):
        """
        Returns: list of n dictionaries, where keys are species.
        """
        species_names = self.model.getFloatingSpeciesConcentrationIds()
        species_values = self.model.getFloatingSpeciesConcentrations()

        base_mean = 50
        base_std_dev = 15

        random_concentrations = []
        for _ in range(self.n_initial_conditions):
            iteration_concentrations = {}

            for name, value in zip(species_names, species_values):
                if value == 0:
                    iteration_concentrations[name] = max(
                        0, round(np.random.normal(base_mean, base_std_dev))
                    )
                else:
                    low = max(0, value / 2)
                    high = value * 2
                    iteration_concentrations[name] = round(np.random.uniform(low, high))

                iteration_concentrations[name] = float(iteration_concentrations[name])

            random_concentrations.append(iteration_concentrations)

        return random_concentrations

    def randomize_parameters(self, sigma=0.1):
        """
        Returns: list of n dictionaries, where keys are parameters.
        """
        parameter_names = self.model.getGlobalParameterIds()
        parameter_values = self.model.getGlobalParameterValues()

        random_parameters = []
        num_parameters = len(parameter_names)

        for i in range(self.n_initial_conditions):
            iteration_parameters = {}

            for j, (name, value) in enumerate(zip(parameter_names, parameter_values)):
                if i % num_parameters == j:
                    shift = np.random.uniform(-sigma, sigma) * value
                    iteration_parameters[name] = value + shift
                else:
                    # keep the default value for other parameters
                    iteration_parameters[name] = value

            random_parameters.append(iteration_parameters)

        return random_parameters

    def assign_custom_values_to_model(self, value_dict):
        """
        value_dict: can be species concentrations, parameters values, etc.
        Returns: the model with assigned values.
        """
        for prop_name, prop_value in value_dict.items():
            self.model[prop_name] = prop_value

    def get_variable_names(self):
        names = ["time"]
        names.extend(self.model.getFloatingSpeciesConcentrationIds())
        names.extend(self.model.getGlobalParameterIds())

        return names

    def get_species_names(self):
        return self.model.getFloatingSpeciesConcentrationIds()

    def get_num_parameters(self):
        return len(self.get_randomized_params_dict().keys())

    def get_initial_concentrations_array(self):
        return np.array([list(d.values()) for d in self.init_concentrations])

    def get_randomized_params_dict(self):
        params = {}
        for d in self.randomized_parameters:
            for k, v in d.items():
                if k not in params:
                    params[k] = []
                params[k].append(v)
        return params

    def get_merged_concentrations_and_params(self):
        keys = list(self.randomized_parameters[0].keys())
        new_rows = []

        for param_dict, row in zip(
            self.randomized_parameters, self.get_initial_concentrations_array()
        ):
            new_row = np.append(row, [param_dict[key] for key in keys])
            new_rows.append(new_row)

        new_concentrations = np.array(new_rows)

        return new_concentrations

    def extract_species_concentrations_from_init_condition_dict(
        self, init_consition_dict
    ):
        return np.array(list(init_consition_dict.values())).squeeze()
