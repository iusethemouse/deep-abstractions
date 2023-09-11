import knime.extension as knext

import tellurium as te
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
import logging

from utils.port_objects import (
    crn_definition_port_type,
    CrnDefinitionSpec,
    CrnDefinitionPortObject,
)

from utils.categories import simulations_category
from utils.simulation_manager import SimulationManager

te.setDefaultPlottingEngine("matplotlib")

LOGGER = logging.getLogger(__name__)


@knext.node(
    name="Stochastic Simulator",
    node_type=knext.NodeType.MANIPULATOR,
    icon_path="src/assets/icons/icon.png",
    category=simulations_category,
)
@knext.input_port(
    name="CRN Definition",
    description="The CRN model to perform the simulation on.",
    port_type=crn_definition_port_type,
)
@knext.output_table(
    name="Simulation traces",
    description="Table containing the vertically-stacked simulation traces.",
)
@knext.output_image(
    name="Simulation traces PNG image",
    description="Image representing the produced simulation traces.",
)
@knext.output_view(
    name="Simulation traces view",
    description="Interactive view of the produced simulation traces.",
)
class StochasticSimulator:
    """
    This node allows to simulate the provided CRN model using the Gillespie algorithm.

    The simulation results are returned as a KNIME table, and the trajectories are plotted and shown as
    a PNG image as well as an interactive view of the node.
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

    n_simulations = knext.IntParameter(
        label="Number of simulations",
        description="Number of simulations to perform for the given initial condition.",
        default_value=50,
        min_value=1,
    )

    random_seed = knext.IntParameter(
        label="Random seed",
        description="If set to non-zero, it will be used to enable reproducible simulations.",
        default_value=0,
        is_advanced=True,
    )

    def configure(
        self, config_context: knext.ConfigurationContext, input_spec: CrnDefinitionSpec
    ):
        species_names = input_spec.spec_data["species"]
        col_names = ["time"] + species_names
        types = [knext.double()] * len(col_names)
        return (
            knext.Schema(ktypes=types, names=col_names),
            knext.ImagePortObjectSpec(knext.ImageFormat.PNG),
        )

    def execute(
        self,
        exec_context: knext.ExecutionContext,
        input_port_object: CrnDefinitionPortObject,
    ):
        ant_definition = input_port_object.data
        sm = SimulationManager(ant_definition)
        sm.set_model_parameters(
            1,
            self.n_simulations,
            self.start_time,
            self.end_time,
            self.n_steps,
            self.random_seed,
        )

        init_conditions = sm.get_randomized_initial_conditions(
            zero_perturb_prob=1.0, n_conditions=1
        )
        data = sm.simulate(init_conditions, exec_context)
        png_bytes = sm.plot_simulations(
            data,
            1,
            self.n_simulations,
            sm.get_column_names(),
        )

        col_names = ["time"] + sm.get_species_names()
        n_cols = len(col_names)
        reshaped_sum = data.reshape(self.n_simulations * (self.n_steps + 1), n_cols)
        df = pd.DataFrame(reshaped_sum, columns=col_names)

        return (
            knext.Table.from_pandas(df),
            png_bytes.getvalue(),
            knext.view_matplotlib(),
        )
