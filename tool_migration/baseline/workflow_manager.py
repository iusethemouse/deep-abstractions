import torch
import torch.nn as nn
from torch.utils.data import DataLoader

import numpy as np

from data_manager import DataManager, DataWrapper
from model_manager import DeepAbstraction

device = torch.device("mps")


class WorkflowManager:
    def init_data_manager(
        self,
        scrn_filepath="example.xml",
        n_initial_conditions=10,
        n_simulations_per_condition=10,
    ):
        self.data_manager = DataManager(
            scrn_filepath,
            n_initial_conditions,
            n_simulations_per_condition,
        )

    def init_deep_abstraction(self):
        self.deep_abstraction = DeepAbstraction(
            input_size=len(self.data_manager.get_variable_names()),
            hidden_size=50,
            num_layers=2,
            output_size=len(self.data_manager.get_species_names()),
        )
        self.deep_abstraction.to(device)

    def generate_simulation_data(self):
        self.simulation_data = self.data_manager.simulate()
        print(f">> generated simulation data, shape: {self.simulation_data.shape}")

    def save_simulation_data(self, filepath="sim_data"):
        np.save(filepath, self.simulation_data)
        print(f">> saved simulation data to {filepath}.npy")

    def load_simulation_data(self, filepath="sim_data.npy"):
        self.simulation_data = np.load("sim_data.npy")
        print(
            f">> loaded simulation data from {filepath}, shape: {self.simulation_data.shape}"
        )

    def prepare_data_loaders(self, batch_size=64, split=0.8):
        split_index = int(len(self.simulation_data) * split)
        train_data = self.simulation_data[:split_index]
        test_data = self.simulation_data[split_index:]

        train_dataset = DataWrapper(train_data)
        test_dataset = DataWrapper(test_data)

        self.train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True
        )
        self.test_loader = DataLoader(
            test_dataset, batch_size=batch_size, shuffle=False
        )
        print(
            ">> split simulation data into train and test sets, prepared data loaders"
        )

    def save_deep_abstraction(self, filepath="model_state_dict.pth"):
        torch.save(self.deep_abstraction.state_dict(), filepath)
        print(f">> saved deep abstraction model to {filepath}")

    def load_deep_abstraction(self, filepath="model_best_state_dict.pth"):
        self.deep_abstraction.load_state_dict(torch.load("model_best_state_dict.pth"))
        self.deep_abstraction.to(device)
        print(f">> loaded deep abstraction model from {filepath}")

    def train_deep_abstraction(
        self,
        n_epochs=20,
        loss_criterion=nn.MSELoss(),
        patience=5,
    ):
        optimizer = torch.optim.Adam(self.deep_abstraction.parameters())

        # train model
        best_loss = float("inf")
        epochs_no_improve = 0

        print(">> commencing deep abstraction training")
        for epoch in range(n_epochs):
            for i, (inputs, targets) in enumerate(self.train_loader):
                inputs = inputs.to(device)
                targets = targets.to(device)

                outputs = self.deep_abstraction(inputs)
                loss = loss_criterion(outputs, targets)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            print(f"Epoch [{epoch+1}/{n_epochs}], Loss: {loss.item():.4f}")

            if loss.item() < best_loss:
                best_loss = loss.item()
                epochs_no_improve = 0
                torch.save(
                    self.deep_abstraction.state_dict(), "model_best_state_dict.pth"
                )
            else:
                epochs_no_improve += 1

            if epochs_no_improve == patience:
                print("Early stopping due to no improvement in loss.")
                break

        print(">> trained and saved model")

    def validate_deep_abstraction(self):
        self.deep_abstraction.eval()
        running_loss = 0.0
        criterion = nn.MSELoss()
        with torch.no_grad():
            for i, (inputs, targets) in enumerate(self.test_loader):
                inputs = inputs.float().to(device)
                targets = targets.float().to(device)

                outputs = self.deep_abstraction(inputs).round()

                loss = criterion(outputs, targets)
                running_loss += loss.item()

        average_loss = running_loss / len(self.test_loader)
        print(f"Validation Loss (MSE) of the model on test data : {average_loss}")

    def get_random_index_for_initial_condition(self):
        init_conditions = self.data_manager.get_initial_concentrations_array()
        return np.random.randint(0, len(init_conditions))

    def get_random_initial_condition(self, random_index=None):
        """
        Returns a randomly sampled array of initial species concentrations.
        """
        init_conditions = self.data_manager.get_initial_concentrations_array()
        if random_index == None:
            random_index = self.get_random_index_for_initial_condition()

        return init_conditions[random_index]

    def prepare_initial_condition_for_input(
        self, init_condition, random_index=None, timestamp=0.0, params_dict=None
    ):
        """
        Prepends a timestamp and appends reaction rates to a provided array of species concentrations.
        """
        if random_index == None:
            random_index = self.get_random_index_for_initial_condition()

        if params_dict == None:
            params_dict = self.data_manager.get_randomized_params_dict()

        params = []
        param_names = params_dict.keys()
        for param_name in param_names:
            params.append(params_dict[param_name][random_index])

        i = np.concatenate(([timestamp], init_condition))
        i = np.append(i, params)
        i = torch.from_numpy(i).float().to(device)
        i = torch.unsqueeze(i, 0)
        i = torch.unsqueeze(i, 0)  # emulate a batch of size 1
        return i

    def get_random_initial_state(self, random_index=None):
        if random_index == None:
            random_index = self.get_random_index_for_initial_condition()
        init_condition = self.get_random_initial_condition(random_index)
        return self.prepare_initial_condition_for_input(init_condition, random_index)

    def convert_tensors_to_numpy(self, tensors):
        return np.array(
            [tensor.squeeze().detach().cpu().numpy() for tensor in tensors]
        )[np.newaxis, :]

    def combine_numpy_arrays(self, arrays):
        return np.concatenate(arrays, axis=0)

    def predict_next_state(self, current_state=None):
        if current_state == None:
            current_state = self.get_random_initial_state()

        pred = self.deep_abstraction(current_state).round()
        return pred

    def produce_chain_of_states(
        self, n_steps=10, random_index=None, initial_state=None
    ):
        if random_index == None and initial_state == None:
            random_index = self.get_random_index_for_initial_condition()
            initial_state = self.get_random_initial_state(random_index)
        current_state = initial_state
        trajectories = [current_state]
        timestamp = 0.1
        timestep = 0.1
        for i in range(n_steps):
            next_state = self.predict_next_state(current_state)
            next_state_array = next_state.squeeze().detach().cpu().numpy()

            current_state = self.prepare_initial_condition_for_input(
                next_state_array, random_index, timestamp
            )
            timestamp += timestep
            trajectories.append(current_state)

        return trajectories
