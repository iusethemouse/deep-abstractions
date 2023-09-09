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
from utils.mdn_manager import MdnManager
from utils.simulation_manager import SimulationManager

te.setDefaultPlottingEngine("matplotlib")

LOGGER = logging.getLogger(__name__)
ZERO_PERTURB_RANGE = (0, 10)


@knext.node(
    name="Deep Abstraction Simulator",
    node_type=knext.NodeType.PREDICTOR,
    icon_path="src/assets/icons/icon.png",
    category=deep_abstractions_category,
)
# @knext.input_port(
#     name="CRN Definition",
#     description="",
#     port_type=crn_definition_port_type,
# )
@knext.input_port(
    name="Trained Deep Abstraction Model",
    description="Object containing a trained deep abstract model.",
    port_type=deep_abstraction_model_port_type,
)
@knext.output_table(
    name="Simulation traces",
    description="Trajectories generated by the deep abstract model.",
)
@knext.output_view(
    name="Simulation traces view",
    description="Interactive view of the produced simulation traces.",
)
class DeepAbstractionSimulator:
    n_init_conditions = knext.IntParameter(
        label="Number of initial conditions",
        description="Number of simulations to perform for the given initial condition.",
        default_value=10,
        min_value=1,
    )

    n_sims_per_init_condition = knext.IntParameter(
        label="Number of simulations per initial condition",
        description="Number of simulations to perform for each initial condition.",
        default_value=10,
        min_value=1,
    )

    n_steps = knext.IntParameter(
        label="Number of steps per simulation",
        description="Number of simulation steps to perform for each simulation.",
        default_value=10,
        min_value=1,
    )

    end_time = knext.DoubleParameter(
        label="End time",
        description="Time at which to stop the simulation.",
        default_value=50.0,
        min_value=0.1,
    )

    variance_range = knext.DoubleParameter(
        label="Variance degree",
        description="The degree of the random perturbation to apply to the initial conditions.",
        default_value=0.1,
        min_value=0.0,
        max_value=1.0,
    )

    zero_perturb_prob = knext.DoubleParameter(
        label="Zero perturbation probability",
        description="Probability of replacing a species with a zero initial concentration with a random value.",
        default_value=0.9,
        min_value=0.0,
        max_value=1.0,
    )

    def configure(
        self,
        config_context: knext.ConfigurationContext,
        input_spec: DeepAbstractionModelSpec,
    ):
        species_names = input_spec.spec_data["species"]
        col_names = ["time"] + species_names
        types = [knext.double()] * len(col_names)

        return knext.Schema(ktypes=types, names=col_names)

    def execute(
        self,
        exec_context: knext.ExecutionContext,
        input_port_object: DeepAbstractionModelPortObject,
    ):
        ant_definition = input_port_object.spec.spec_data["antimony_definition"]
        sm = SimulationManager(ant_definition)

        sim_config = input_port_object.spec.spec_data["simulation_configuration"]
        # n_init_conditions = sim_config["n_init_conditions"]
        # n_sims_per_init_condition = sim_config["n_sims_per_init_condition"]
        start_time = sim_config["start_time"]
        end_time = sim_config["end_time"]
        n_steps = sim_config["n_steps"]
        time_step = (
            end_time / n_steps
        )  # calculate the time step based on the original CRN configuration

        sm.set_model_parameters(
            self.n_init_conditions,
            self.n_sims_per_init_condition,
            start_time,
            self.end_time,
            self.n_steps,  # using the provided n_steps instead of the original here
        )

        mm = MdnManager(sm.get_num_species())
        model_weights = input_port_object.data["model_weights"]
        mm.set_model_weights(model_weights)

        init_conditions = sm.get_randomized_initial_conditions(
            range_percentage=self.variance_range,
            zero_perturb_prob=self.zero_perturb_prob,
            zero_perturb_range=ZERO_PERTURB_RANGE,
            n_conditions=self.n_init_conditions,
        )
        init_conditions = sm.add_time_column(init_conditions)

        mdn_data = mm.simulate(
            init_conditions,
            exec_context,
            time_step,
            self.n_steps,
            self.n_sims_per_init_condition,
        )

        sm.plot_simulations(
            # f"plots/{config_name}__mdn",
            mdn_data,
            self.n_init_conditions,
            self.n_sims_per_init_condition,
            sm.get_column_names(),
        )

        col_names = ["time"] + sm.get_species_names()
        n_cols = len(col_names)

        mdn_data = mdn_data.reshape(
            self.n_init_conditions
            * self.n_sims_per_init_condition
            * (self.n_steps + 1),
            n_cols,
        )
        df = pd.DataFrame(mdn_data, columns=col_names)

        return (knext.Table.from_pandas(df), knext.view_matplotlib())
