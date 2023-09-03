import knime.extension as knext

import tellurium as te
import logging
import pandas as pd

from utils.port_objects import (
    crn_definition_port_type,
    CrnDefinitionSpec,
    CrnDefinitionPortObject,
)

from utils.port_objects import (
    simulation_data_port_type,
    SimulationDataSpec,
    SimulationDataPortObject,
)

from utils.categories import simulations_category
from utils.workflow_manager import WorkflowManager

LOGGER = logging.getLogger(__name__)


@knext.node(
    name="Training Data Generator",
    node_type=knext.NodeType.MANIPULATOR,
    icon_path="src/assets/icons/icon.png",
    category=simulations_category,
)
@knext.input_port(
    name="SRN Definition",
    description="",
    port_type=crn_definition_port_type,
)
@knext.output_port(
    name="Training simulation data", description="", port_type=simulation_data_port_type
)
class TrainingDataGenerator:
    end_time = knext.DoubleParameter(
        label="End time", description="", default_value=50.0, min_value=0.1
    )

    n_steps = knext.IntParameter(
        label="Steps per simulation", description="", default_value=100, min_value=1
    )

    n_init_conditions = knext.IntParameter(
        label="Number of initial conditions",
        description="",
        default_value=100,
        min_value=1,
    )

    n_sims_per_init_conditions = knext.IntParameter(
        label="Simulations per initial condition",
        description="",
        default_value=10,
        min_value=1,
    )

    def configure(
        self, config_context: knext.ConfigurationContext, input_spec: CrnDefinitionSpec
    ):
        return SimulationDataSpec(dict())

    def execute(
        self,
        exec_context: knext.ExecutionContext,
        input_port_object: CrnDefinitionPortObject,
    ):
        definition = input_port_object.data

        # initialise all components
        wf_manager = WorkflowManager()
        wf_manager.init_data_manager(
            scrn_definition=definition,
            n_initial_conditions=self.n_init_conditions,
            n_simulations_per_condition=self.n_sims_per_init_conditions,
            steps=self.n_steps,
            endtime=self.end_time,
        )
        wf_manager.init_deep_abstraction()

        # perform data generation
        wf_manager.generate_simulation_data()

        data = {
            "srn_definition": definition,
            "training_data": wf_manager.simulation_data,
            "simulation_configuration": {
                "n_init_conditions": self.n_init_conditions,
                "n_sims_per_init_conditions": self.n_sims_per_init_conditions,
                "n_steps": self.n_steps,
                "endtime": self.end_time,
            },
        }

        return SimulationDataPortObject(SimulationDataSpec(dict()), data)
