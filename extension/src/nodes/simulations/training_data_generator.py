import knime.extension as knext

import logging

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
from utils.simulation_manager import SimulationManager

LOGGER = logging.getLogger(__name__)
ZERO_PERTURB_RANGE = (0, 10)


@knext.node(
    name="Training Data Generator",
    node_type=knext.NodeType.MANIPULATOR,
    icon_path="src/assets/icons/icon.png",
    category=simulations_category,
)
@knext.input_port(
    name="CRN Definition",
    description="The CRN model to produce the training data for.",
    port_type=crn_definition_port_type,
)
@knext.output_port(
    name="Training simulation data",
    description="Object containing the generated training data.",
    port_type=simulation_data_port_type,
)
class TrainingDataGenerator:
    """
    This node allows to generate training data for the provided CRN model. The process differs
    from the Stochastic Simulator node in that the initial conditions are randomly varied to cover a predefined
    range. The generated training data has a shape of (n_init_conditions * n_sims_per_init_conditions, n_steps, n_species + 1).

    The training data can then be used to train a deep abstract model.
    """

    start_time = knext.DoubleParameter(
        label="Start time",
        description="Time from which to start the simulation.",
        default_value=0.0,
    )

    end_time = knext.DoubleParameter(
        label="End time",
        description="Time at which to stop the simulation.",
        default_value=50.0,
        min_value=0.1,
    )

    n_steps = knext.IntParameter(
        label="Steps",
        description="Number of steps to perform during the specified span of time.",
        default_value=50,
        min_value=1,
    )

    n_init_conditions = knext.IntParameter(
        label="Number of initial conditions",
        description="The initial conditions encoded in the CRN definition will be randomly varied to produce this many initial conditions.",
        default_value=100,
        min_value=1,
    )

    n_sims_per_init_condition = knext.IntParameter(
        label="Simulations per initial condition",
        description="Number of simulations to perform per initial condition.",
        default_value=10,
        min_value=1,
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
        self, config_context: knext.ConfigurationContext, input_spec: CrnDefinitionSpec
    ):
        return SimulationDataSpec(dict())

    def execute(
        self,
        exec_context: knext.ExecutionContext,
        input_port_object: CrnDefinitionPortObject,
    ):
        ant_definition = input_port_object.data
        sm = SimulationManager(ant_definition)
        sm.set_model_parameters(
            self.n_init_conditions,
            self.n_sims_per_init_condition,
            self.start_time,
            self.end_time,
            self.n_steps,
        )

        init_conditions = sm.get_randomized_initial_conditions(
            range_percentage=self.variance_range,
            zero_perturb_prob=self.zero_perturb_prob,
            zero_perturb_range=ZERO_PERTURB_RANGE,
        )

        data = sm.simulate(init_conditions, exec_context)
        data_spec = {
            "species": sm.get_species_names(),
            "parameters": sm.get_parameter_names(),
            "antimony_definition": ant_definition,
            "simulation_configuration": {
                "n_init_conditions": self.n_init_conditions,
                "n_sims_per_init_condition": self.n_sims_per_init_condition,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "n_steps": self.n_steps,
            },
        }

        return SimulationDataPortObject(SimulationDataSpec(data_spec), data)
