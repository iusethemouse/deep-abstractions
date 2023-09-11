import knime.extension as knext

import logging
from pathlib import Path
import pickle

from utils.port_objects import (
    deep_abstraction_model_port_type,
    DeepAbstractionModelSpec,
    DeepAbstractionModelPortObject,
)

from utils.categories import deep_abstractions_category

from utils.mdn_manager import MdnManager
from utils.simulation_manager import SimulationManager

LOGGER = logging.getLogger(__name__)
DEFAULT_WRITE_PATH = "/Users/ivan/Downloads/tmp/"
DEFAULT_FILENAME = "abstract_model"


@knext.node(
    name="Deep Abstraction Writer",
    node_type=knext.NodeType.SINK,
    icon_path="src/assets/icons/icon.png",
    category=deep_abstractions_category,
)
@knext.input_port(
    name="Trained abstraction model",
    description="Trained deep abstract model to be written to a file.",
    port_type=deep_abstraction_model_port_type,
)
class DeepAbstractionWriter:
    """
    Writes a trained deep abstract model to the specified local file.

    The provided deep abstract model can be stored locally either in the form of its wieghts, or as an ONNX model.
    """

    class AvailableFormats(knext.EnumParameterOptions):
        WEIGHTS = (
            "PyTorch weights",
            "Save the PyTorch model weights together with the CRN metadata. Can be read by the Reader node.",
        )
        ONNX = (
            "ONNX",
            "Save the model in the universal ONNX format.",
        )

    format_selection = knext.EnumParameter(
        label="Output format",
        description="Specify the format to use for the output file.",
        default_value=AvailableFormats.WEIGHTS.name,
        enum=AvailableFormats,
    )

    filename = knext.StringParameter(
        label="Output filename",
        description="What to name the saved file.",
        default_value=DEFAULT_FILENAME,
    )

    destination = knext.StringParameter(
        label="Output directory",
        description="Where to place the saved file.",
        default_value=DEFAULT_WRITE_PATH,
    )

    def configure(
        self,
        config_context: knext.ConfigurationContext,
        input_spec: DeepAbstractionModelSpec,
    ):
        return

    def execute(
        self,
        exec_context: knext.ExecutionContext,
        input_port_object: DeepAbstractionModelPortObject,
    ):
        # check that the destionation directory exists and create it if it doesn't
        Path(self.destination).mkdir(parents=True, exist_ok=True)

        ant_definition = input_port_object.spec.spec_data["antimony_definition"]
        sm = SimulationManager(ant_definition)
        mm = MdnManager(sm.get_num_species())

        model_weights = input_port_object.data["model_weights"]

        if self.format_selection == self.AvailableFormats.WEIGHTS.name:
            data = {
                "antimony_definition": ant_definition,
                "simulation_configuration": input_port_object.spec.spec_data[
                    "simulation_configuration"
                ],
                "model_weights": model_weights,
            }

            with open(Path(self.destination).joinpath(self.filename), "wb") as f:
                pickle.dump(data, f)
        elif self.format_selection == self.AvailableFormats.ONNX.name:
            mm.set_model_weights(model_weights)
            mm.save_model_to_onnx(
                Path(self.destination).joinpath(self.filename + ".onnx")
            )

        return
