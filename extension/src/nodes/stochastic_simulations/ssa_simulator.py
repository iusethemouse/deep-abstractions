import knime.extension as knext

import tellurium as te
import pandas as pd

from utils.port_objects import (
    scrn_definition_port_type,
    ScrnDefinitionSpec,
    ScrnDefinitionPortObject,
)

from utils.port_objects import (
    simulation_data_port_type,
    SimulationDataSpec,
    SimulationDataPortObject,
)

from utils.categories import stochastic_simulations_category

te.setDefaultPlottingEngine("matplotlib")


@knext.node(
    name="Stochastic Simulator",
    node_type=knext.NodeType.MANIPULATOR,
    icon_path="src/assets/icons/icon.png",
    category=stochastic_simulations_category,
)
@knext.input_port(
    name="SCRN Definition",
    description="",
    port_type=scrn_definition_port_type,
)
@knext.output_port(
    name="Simulation Data", description="", port_type=simulation_data_port_type
)
@knext.output_view(name="Simulation view", description="")
class StochasticSimulator:
    start_time = knext.DoubleParameter(
        label="Start time", description="", default_value=0.0
    )

    end_time = knext.DoubleParameter(
        label="End time", description="", default_value=10.0
    )

    trajectories = knext.IntParameter(
        label="Number of trajectories", description="", default_value=100
    )

    random_seed = knext.IntParameter(
        label="Random seed", description="", default_value=1234
    )

    steps = knext.IntParameter(label="Number of steps", description="", default_value=0)

    def configure(
        self, config_context: knext.ConfigurationContext, input_spec: ScrnDefinitionSpec
    ):
        spec_data = input_spec.spec_data
        spec_data["sim_configuration"] = {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "trajectories": self.trajectories,
            "random_seed": self.random_seed,
        }
        return SimulationDataSpec(spec_data)

    def execute(
        self,
        exec_context: knext.ExecutionContext,
        input_port_object: ScrnDefinitionPortObject,
    ):
        spec_data = input_port_object.spec.spec_data
        spec_data["sim_configuration"] = {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "trajectories": self.trajectories,
            "random_seed": self.random_seed,
        }

        definition = input_port_object.data
        r = te.loadAntimonyModel(definition)

        r.integrator = "gillespie"
        r.integrator.seed = self.random_seed

        progress = 0
        progress_step = 100 / self.trajectories / 100
        results = []
        for _ in range(0, self.trajectories):
            exec_context.set_progress(progress)
            r.reset()
            if self.steps > 0:
                s = r.simulate(self.start_time, self.end_time, self.steps)
            else:
                s = r.simulate(self.start_time, self.end_time)
            results.append(s)
            r.plot(s, show=False, alpha=0.7)
            progress += progress_step
        te.show()

        return (
            SimulationDataPortObject(SimulationDataSpec(spec_data), results),
            knext.view_matplotlib(),
        )
