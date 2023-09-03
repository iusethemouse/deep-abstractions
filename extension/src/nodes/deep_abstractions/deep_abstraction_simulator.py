import knime.extension as knext

import tellurium as te
import pandas as pd
import logging

from utils.port_objects import (
    crn_definition_port_type,
    CrnDefinitionSpec,
    CrnDefinitionPortObject,
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
    name="Deep Abstraction Simulator",
    node_type=knext.NodeType.PREDICTOR,
    icon_path="src/assets/icons/icon.png",
    category=deep_abstractions_category,
)
@knext.input_port(
    name="CRN Definition",
    description="",
    port_type=crn_definition_port_type,
)
@knext.input_port(
    name="Trained Deep Abstraction Model",
    description="",
    port_type=deep_abstraction_model_port_type,
)
@knext.output_table(
    name="Simulation traces",
    description="",
)
class DeepAbstractionSimulator:
    n_sims = knext.IntParameter(
        label="Number simulations", description="", default_value=1, min_value=1
    )

    n_steps = knext.IntParameter(
        label="Number of steps per simulation",
        description="",
        default_value=10,
        min_value=1,
    )

    def configure(
        self,
        config_context: knext.ConfigurationContext,
        input_spec_crn: CrnDefinitionSpec,
        input_spec_da: DeepAbstractionModelSpec,
    ):
        species_names = input_spec_crn.spec_data["species"]  # model definition
        col_names = ["time"] + species_names
        types = [knext.double()] * len(col_names)

        return knext.Schema(ktypes=types, names=col_names)

    def execute(
        self,
        exec_context: knext.ExecutionContext,
        input_port_object_crn: CrnDefinitionPortObject,
        input_port_object_da: DeepAbstractionModelPortObject,
    ):
        crn_definition = input_port_object_crn.data
        sim_configuration = input_port_object_da.data["simulation_configuration"]
        model_weights = input_port_object_da.data["model_weights"]

        wf_manager = WorkflowManager()
        wf_manager.init_data_manager(
            crn_definition=crn_definition,
            n_initial_conditions=sim_configuration["n_init_conditions"],
            n_simulations_per_condition=sim_configuration["n_sims_per_init_conditions"],
            steps=sim_configuration["n_steps"],
            endtime=sim_configuration["endtime"],
        )
        wf_manager.init_deep_abstraction()

        wf_manager.load_deep_abstraction_weights(model_weights)

        sims = []
        timestep = sim_configuration["endtime"] / sim_configuration["n_steps"]
        n_params = wf_manager.data_manager.get_num_parameters()

        for i in range(self.n_sims):
            tensor_trajectories = wf_manager.produce_chain_of_states(
                self.n_steps, timestep=timestep
            )
            numpy_trajectories = wf_manager.convert_tensors_to_numpy(
                tensor_trajectories
            ).squeeze()
            numpy_trajectories = numpy_trajectories[:, :-n_params]
            sims.append(numpy_trajectories)

        sims = wf_manager.combine_numpy_arrays(sims)

        species_names = input_port_object_crn.spec.spec_data["species"]
        col_names = ["time"] + species_names
        df = pd.DataFrame(sims, columns=col_names)

        return knext.Table.from_pandas(df)
