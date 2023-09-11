import knime.extension as knext

import tellurium as te
import logging

from utils.port_objects import (
    simulation_data_port_type,
    SimulationDataSpec,
    SimulationDataPortObject,
)

from utils.port_objects import (
    deep_abstraction_model_port_type,
    DeepAbstractionModelSpec,
    DeepAbstractionModelPortObject,
)

from utils.categories import deep_abstractions_category
from utils.simulation_manager import SimulationManager
from utils.mdn_manager import MdnManager

te.setDefaultPlottingEngine("matplotlib")

LOGGER = logging.getLogger(__name__)


@knext.node(
    name="Deep Abstraction Learner",
    node_type=knext.NodeType.LEARNER,
    icon_path="src/assets/icons/icon.png",
    category=deep_abstractions_category,
)
@knext.input_port(
    name="Training data",
    description="CRN simulation data generated using SSA and used for training.",
    port_type=simulation_data_port_type,
)
@knext.output_port(
    name="Trained Deep Abstract Model",
    description="The trained deep abstract model.",
    port_type=deep_abstraction_model_port_type,
)
class DeepAbstractionLearner:
    """
    Learns a deep abstract model from CRN simulation data.

    A well-trained deep abstract model can be used to efficiently produce new CRN trajectories that follow the CRN dynamics
    encoded in the training data.
    """

    n_epochs = knext.IntParameter(
        label="Number of epochs",
        description="""
        The number of epochs to train the deep abstract model for.
        
        An epoch is a single pass through the entire training set.
        Usually, the model's performance increases with the number of epochs, but then
        decreases as the model begins to overfit the training data.""",
        default_value=20,
        min_value=1,
    )

    patience = knext.IntParameter(
        label="Training patience",
        description="""
        The number of epochs to wait before early stopping.
        
        Early stopping is a form of regularisation used to avoid overfitting.""",
        default_value=8,
        min_value=1,
        is_advanced=True,
    )

    batch_size = knext.IntParameter(
        label="Batch size",
        description="""
        The number of training examples in one forward/backward pass.
        
        The higher the batch size, the more available memory is required.""",
        default_value=128,
        min_value=1,
        is_advanced=True,
    )

    def configure(
        self, config_context: knext.ConfigurationContext, input_spec: SimulationDataSpec
    ):
        return DeepAbstractionModelSpec(dict())

    def execute(
        self,
        exec_context: knext.ExecutionContext,
        input_port_object: SimulationDataPortObject,
    ):
        training_data = input_port_object.data
        ant_definition = input_port_object.spec.spec_data["antimony_definition"]
        sm = SimulationManager(ant_definition)

        sim_config = input_port_object.spec.spec_data["simulation_configuration"]
        n_init_conditions = sim_config["n_init_conditions"]
        n_sims_per_init_condition = sim_config["n_sims_per_init_condition"]
        start_time = sim_config["start_time"]
        end_time = sim_config["end_time"]
        n_steps = sim_config["n_steps"]
        step_size = end_time / n_steps

        sm.set_model_parameters(
            n_init_conditions,
            n_sims_per_init_condition,
            start_time,
            end_time,
            n_steps,
        )

        mm = MdnManager(sm.get_num_species())
        mm.load_data(training_data)
        mm.prepare_data_loaders(batch_size=self.batch_size)
        mm.train(
            exec_context=exec_context, n_epochs=self.n_epochs, patience=self.patience
        )

        data = {
            "model_weights": mm.get_model_weights(),
        }

        # formulate the new sim_config only containing the start_time and step_size
        sim_config = {
            "step_size": step_size,
        }
        spec_data = input_port_object.spec.spec_data
        spec_data["simulation_configuration"] = sim_config

        return DeepAbstractionModelPortObject(
            # DeepAbstractionModelSpec(input_port_object.spec.spec_data), data
            DeepAbstractionModelSpec(spec_data),
            data,
        )
