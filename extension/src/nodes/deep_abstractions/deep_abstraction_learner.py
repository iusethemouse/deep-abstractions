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
from utils.workflow_manager import WorkflowManager

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
    description="",
    port_type=simulation_data_port_type,
)
@knext.output_port(
    name="Trained Deep Abstraction Model",
    description="",
    port_type=deep_abstraction_model_port_type,
)
class DeepAbstractionLearner:
    n_epochs = knext.IntParameter(
        label="Number of epochs", description="", default_value=20, min_value=1
    )

    patience = knext.IntParameter(
        label="Training patience",
        description="",
        default_value=8,
        min_value=1,
        is_advanced=True,
    )

    batch_size = knext.IntParameter(
        label="Batch size",
        description="",
        default_value=64,
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
        srn_definition = input_port_object.data["srn_definition"]
        training_data = input_port_object.data["training_data"]
        sim_configuration = input_port_object.data["simulation_configuration"]

        wf_manager = WorkflowManager()
        wf_manager.init_data_manager(
            scrn_definition=srn_definition,
            n_initial_conditions=sim_configuration["n_init_conditions"],
            n_simulations_per_condition=sim_configuration["n_sims_per_init_conditions"],
            steps=sim_configuration["n_steps"],
            endtime=sim_configuration["endtime"],
        )
        wf_manager.init_deep_abstraction()
        wf_manager.load_simulation_data_from_memory(training_data)
        wf_manager.prepare_data_loaders(batch_size=self.batch_size)

        wf_manager.train_deep_abstraction(
            exec_context, n_epochs=self.n_epochs, patience=self.patience
        )
        wf_manager.validate_deep_abstraction()

        data = {
            "model_weights": wf_manager.export_deep_abstraction_weights(),
            "srn_definition": srn_definition,
            "simulation_configuration": sim_configuration,
        }

        return DeepAbstractionModelPortObject(DeepAbstractionModelSpec(dict()), data)
