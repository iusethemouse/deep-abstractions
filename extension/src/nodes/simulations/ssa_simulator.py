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

te.setDefaultPlottingEngine("matplotlib")

LOGGER = logging.getLogger(__name__)


@knext.node(
    name="Stochastic Simulator",
    node_type=knext.NodeType.MANIPULATOR,
    icon_path="src/assets/icons/icon.png",
    category=simulations_category,
)
@knext.input_port(
    name="SRN Definition",
    description="",
    port_type=crn_definition_port_type,
)
@knext.output_table(
    name="Simulation traces",
    description="",
)
@knext.output_image(
    name="Simulation traces PNG image",
    description="",
)
@knext.output_view(name="Simulation traces view", description="")
class StochasticSimulator:
    start_time = knext.DoubleParameter(
        label="Start time", description="", default_value=0.0
    )

    end_time = knext.DoubleParameter(
        label="End time", description="", default_value=50.0, min_value=0.1
    )

    n_steps = knext.IntParameter(
        label="Steps", description="", default_value=100, min_value=1
    )

    n_simulations = knext.IntParameter(
        label="Number of simulations", description="", default_value=50, min_value=1
    )

    random_seed = knext.IntParameter(
        label="Random seed", description="", default_value=0, is_advanced=True
    )

    def configure(
        self, config_context: knext.ConfigurationContext, input_spec: CrnDefinitionSpec
    ):
        species_names = input_spec.spec_data["species"]  # model definition
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
        definition = input_port_object.data
        r = te.loadAntimonyModel(definition)
        # r = definition
        col_names = ["time"] + r.getBoundarySpeciesIds() + r.getFloatingSpeciesIds()

        r.integrator = "gillespie"
        if self.random_seed != 0:
            r.integrator.seed = self.random_seed

        selections = ["time"] + r.getBoundarySpeciesIds() + r.getFloatingSpeciesIds()
        # n_cols = len(r.selections)
        n_cols = len(col_names)
        s_sum = np.zeros(shape=[self.n_steps, n_cols])
        stacked_sum = np.zeros(shape=[self.n_simulations, self.n_steps, n_cols])

        progress = 0
        progress_step = 100 / self.n_simulations / 100

        for k in range(self.n_simulations):
            exec_context.set_progress(progress)
            r.resetToOrigin()
            s = r.simulate(
                self.start_time, self.end_time, self.n_steps, selections=selections
            )
            s_arr = np.array(s)
            s_sum += s
            stacked_sum[k] = s
            progress += progress_step
            r.plot(s, alpha=0.5, show=False)

        te.plot(
            s[:, 0],
            s_sum[:, 1:] / self.n_simulations,
            names=[x + " (mean)" for x in selections[1:]],
            title="Stochastic simulation",
            xtitle="time",
            ytitle="concentration",
        )
        te.show()

        fig = plt.gcf()
        png_bytes = io.BytesIO()
        fig.savefig(png_bytes, format="png")

        # convert the stacked sum into a dataframe
        reshaped_sum = stacked_sum.reshape(self.n_simulations * self.n_steps, n_cols)
        df = pd.DataFrame(reshaped_sum, columns=col_names)

        return (
            knext.Table.from_pandas(df),
            png_bytes.getvalue(),
            knext.view_matplotlib(),
        )
