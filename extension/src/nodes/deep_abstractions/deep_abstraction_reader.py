import knime.extension as knext

import logging
import pickle

from utils.port_objects import (
    deep_abstraction_model_port_type,
    DeepAbstractionModelSpec,
    DeepAbstractionModelPortObject,
)

from utils.categories import deep_abstractions_category
from utils.simulation_manager import SimulationManager
from utils.mdn_manager import MdnManager

LOGGER = logging.getLogger(__name__)
DEFAULT_PATH = "/Users/ivan/Downloads/tmp/abstract_model"


@knext.node(
    name="Deep Abstraction Reader",
    node_type=knext.NodeType.SOURCE,
    icon_path="src/assets/icons/icon.png",
    category=deep_abstractions_category,
)
@knext.output_port(
    name="Trained Deep Abstract Model",
    description="The loaded trained deep abstract model.",
    port_type=deep_abstraction_model_port_type,
)
class DeepAbstractionReader:
    """
    Reads the PyTorch model weights of a trained deep abstract model from a file.

    The specified file contains the model weights of the abstract model, as well as other related metadata such
    as the CRN definition and the simulation configuration used to generate the training data.
    """

    file_path = knext.StringParameter(
        label="File path",
        description="The path to the local file containing the model weights.",
        default_value=DEFAULT_PATH,
    )

    def configure(self, config_context: knext.ConfigurationContext):
        return DeepAbstractionModelSpec(dict())

    def execute(
        self,
        exec_context: knext.ExecutionContext,
    ):
        # load the pickle file and read in the data
        with open(self.file_path, "rb") as f:
            data = pickle.load(f)
            ant_definition = data["antimony_definition"]
            sim_config = data["simulation_configuration"]
            model_weights = data["model_weights"]

        sm = SimulationManager(ant_definition)
        mm = MdnManager(sm.get_num_species())
        mm.set_model_weights(model_weights)

        data = {
            "model_weights": mm.get_model_weights(),
        }

        spec_data = {
            "species": sm.get_species_names(),
            "parameters": sm.get_parameter_names(),
            "antimony_definition": ant_definition,
            "simulation_configuration": sim_config,
        }

        return DeepAbstractionModelPortObject(DeepAbstractionModelSpec(spec_data), data)
