import knime.extension as knext
from pathlib import Path

from utils.port_objects import (
    crn_definition_port_type,
    CrnDefinitionSpec,
    CrnDefinitionPortObject,
)

from utils.categories import reaction_networks_category
from utils.simulation_manager import SimulationManager

DEFAULT_SBML_PATH = "/path/to/model/definition.xml"


@knext.node(
    name="CRN Reader",
    node_type=knext.NodeType.SOURCE,
    icon_path="src/assets/icons/icon.png",
    category=reaction_networks_category,
)
@knext.output_port(
    name="CRN Definition",
    description="The loaded CRN definition.",
    port_type=crn_definition_port_type,
)
class CrnReader:
    """
    This node allows you to read a CRN definition from a file.

    Supported definition types are *Antimony* (.txt) and *SBML* (.xml).
    """

    file_path = knext.StringParameter(
        label="File path",
        description="The path to the local file containing the CRN definition.",
        default_value=DEFAULT_SBML_PATH,
    )

    def _validate_file_path(self):
        file_extension = Path(self.file_path).suffix
        if file_extension not in [".xml", ".txt"]:
            raise ValueError(
                f"File path {self.file_path} does not end in either .xml or .txt"
            )

    def configure(self, config_context: knext.ConfigurationContext):
        self._validate_file_path()

        # placeholder; actual spec is generated in execute()
        spec_data = dict()

        return CrnDefinitionSpec(spec_data)

    def execute(self, exec_context: knext.ExecutionContext):
        sm = SimulationManager(self.file_path)
        ant_definition = sm.model.getAntimony()
        spec_data = {
            "species": sm.get_species_names(),
            "parameters": sm.get_parameter_names(),
        }

        return CrnDefinitionPortObject(CrnDefinitionSpec(spec_data), ant_definition)
