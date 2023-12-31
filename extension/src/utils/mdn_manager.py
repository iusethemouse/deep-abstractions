import torch
import torch.nn as nn
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

import numpy as np
import platform


def auto_select_device():
    if platform.system() == "Darwin" and platform.processor() == "arm64":
        # M-series Macs
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")


device = auto_select_device()


class GaussianNLLLoss(nn.Module):
    def __init__(self):
        super(GaussianNLLLoss, self).__init__()

    def forward(self, mu, sigma, target):
        neg_log_likelihood = 0.5 * (
            torch.log(sigma**2) + ((target - mu) ** 2) / (sigma**2)
        )
        return neg_log_likelihood.mean()


class DataWrapper(Dataset):
    """
    Used for wrapping raw NumPy data. Training and testing sets should be wrapped separately.
    """

    def __init__(self, data, n_species):
        self.data = data
        self.n_species = n_species

    def __getitem__(self, index):
        """
        Inputs contain all information: time, species concentrations, reaction rates.
        Targets only contain species concentrations.
        """
        # species_concentration_indices = [0, 1, 2]
        species_concentration_indices = list(range(1, self.n_species + 1))

        inputs = self.data[index, :-1, :].astype(np.float32)
        targets = self.data[index, 1:, species_concentration_indices].astype(np.float32)
        targets = np.transpose(targets, (1, 0))

        return (torch.from_numpy(inputs), torch.from_numpy(targets))

    def __len__(self):
        return len(self.data)


class MDN(nn.Module):
    def __init__(
        self, input_size, hidden_size, num_layers, output_size, dropout_rate=0.0
    ):
        super(MDN, self).__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers, batch_first=True, dropout=dropout_rate
        )

        self.fc1 = nn.Linear(hidden_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)

        self.fc_out = nn.Linear(hidden_size, 2 * output_size)  # mu and sigma

        self.relu = nn.ReLU()

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)

        out, _ = self.lstm(x, (h0, c0))

        out = self.fc1(out)
        out = self.relu(out)

        out = self.fc2(out)
        out = self.relu(out)

        out = self.fc_out(out)

        mu, sigma = torch.chunk(out, 2, dim=-1)
        sigma = torch.exp(sigma)

        return mu, sigma


class MdnManager:
    def __init__(self, n_species):
        self.n_species = n_species
        # self.n_parameters = n_parameters

        self.model = MDN(
            # input_size=1 + self.n_species + self.n_parameters,
            input_size=1 + self.n_species,
            hidden_size=50,
            num_layers=2,
            output_size=n_species,
        ).to(device)

    def load_data(self, data):
        self.simulation_data = data

    def prepare_data_loaders(self, batch_size=64, split=0.8):
        split_index = int(len(self.simulation_data) * split)
        train_data = self.simulation_data[:split_index]
        test_data = self.simulation_data[split_index:]

        train_dataset = DataWrapper(train_data, self.n_species)
        test_dataset = DataWrapper(test_data, self.n_species)

        self.train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True
        )
        self.test_loader = DataLoader(
            test_dataset, batch_size=batch_size, shuffle=False
        )

    def save_model(self, filepath):
        torch.save(self.model.state_dict(), filepath)
        print(f"Model saved to {filepath}")

    def load_model(self, filepath):
        self.model.load_state_dict(torch.load(filepath, map_location=device))
        self.model.to(device)  # Move the model to the device
        self.model.eval()
        print(f"Model loaded from {filepath} and moved to {device}")

    def get_model_weights(self):
        return self.model.state_dict()

    def save_model_to_onnx(self, destination):
        dummy_input = torch.randn(1, 1, 1 + self.n_species).to(device)
        torch.onnx.export(self.model, dummy_input, destination, verbose=True)
        print("Model exported to model.onnx")

    def load_onnx_model(self, filepath):
        self.model = torch.jit.load(filepath, map_location=device)
        self.model.to(device)

    def set_model_weights(self, weights):
        self.model.load_state_dict(weights)

    def train(
        self,
        exec_context,
        n_epochs=20,
        # loss_criterion=nn.MSELoss(),
        loss_criterion=GaussianNLLLoss(),
        patience=5,
    ):
        optimizer = torch.optim.Adam(self.model.parameters())

        # train model
        best_loss = float("inf")
        epochs_no_improve = 0

        # progress visualisation
        progress = 0
        progress_step = 100 / n_epochs / 100

        for epoch in range(n_epochs):
            if exec_context.is_canceled():
                print("Execution cancelled.")
                break

            exec_context.set_progress(progress)
            for i, (inputs, targets) in enumerate(self.train_loader):
                inputs = inputs.to(device)
                targets = targets.to(device)

                mu, sigma = self.model(inputs)  # Get mu and sigma
                loss = loss_criterion(mu, sigma, targets)  # Compute Gaussian NLL

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            progress += progress_step

            print(f"Epoch [{epoch+1}/{n_epochs}], Loss: {loss.item():.4f}")

            if loss.item() < best_loss:
                best_loss = loss.item()
                epochs_no_improve = 0
                torch.save(self.model.state_dict(), "model_best_state_dict.pth")
            else:
                epochs_no_improve += 1

            if epochs_no_improve == patience:
                print("Early stopping due to no improvement in loss.")
                break

    def validate(self):
        self.model.eval()
        running_loss = 0.0
        criterion = GaussianNLLLoss()
        with torch.no_grad():
            for i, (inputs, targets) in enumerate(self.test_loader):
                inputs = inputs.float().to(device)
                targets = targets.float().to(device)

                mu, sigma = self.model(inputs)  # Get mu and sigma

                loss = criterion(mu, sigma, targets)
                running_loss += loss.item()

        average_loss = running_loss / len(self.test_loader)
        print(f"Validation Loss of the model on test data : {average_loss}")

    def simulate(
        self,
        init_conditions,
        exec_context,
        time_step,
        n_steps=10,
        n_sims_per_condition=1,
    ):
        self.model.eval()
        all_trajectories = []

        progress = 0
        progress_step = 100 / len(init_conditions) / n_sims_per_condition / 100

        for i, init_condition in enumerate(init_conditions):
            print(
                f"Generating trajectories for init_condition {i+1} / {len(init_conditions)}"
            )

            for sim in range(n_sims_per_condition):
                if exec_context.is_canceled():
                    print("Execution cancelled.")
                    break

                print(f"  Simulating trajectory {sim+1} / {n_sims_per_condition}")
                exec_context.set_progress(progress)

                trajectory = [init_condition[: self.n_species + 1]]
                current_state = self.convert_numpy_to_torch(init_condition)
                timestamp = 0.0

                for j in range(n_steps):
                    mu, sigma = self.model(current_state)  # Get mu and sigma
                    next_state_array = (
                        mu.squeeze().detach().cpu().numpy()
                    )  # Use mu as the next state

                    timestamp += time_step
                    next_state_array = np.concatenate(([timestamp], next_state_array))
                    trajectory.append(np.round(next_state_array))

                    current_state = self.convert_numpy_to_torch(next_state_array)

                trajectory = np.array(trajectory)
                all_trajectories.append(trajectory)

                progress += progress_step

        return np.array(all_trajectories)

    def convert_numpy_to_torch(self, state):
        i = torch.from_numpy(state).float().to(device)
        i = torch.unsqueeze(i, 0)
        i = torch.unsqueeze(i, 0)  # emulate a batch of size 1
        return i
