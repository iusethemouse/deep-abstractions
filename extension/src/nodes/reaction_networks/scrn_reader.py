import knime.extension as knext
import tellurium as te
from pathlib import Path

from utils.port_objects import (
    scrn_definition_port_type,
    ScrnDefinitionSpec,
    ScrnDefinitionPortObject,
)

from utils.categories import reaction_networks_category

DEFAULT_SBML_PATH = "/Users/ivan/Developer/git/deep-abstractions/scrn_models/sir.xml"


@knext.node(
    name="SCRN Reader",
    node_type=knext.NodeType.SOURCE,
    icon_path="src/assets/icons/icon.png",
    category=reaction_networks_category,
)
@knext.output_port(
    name="SCRN Definition",
    description="",
    port_type=scrn_definition_port_type,
)
class ScrnReader:
    file_path = knext.StringParameter(
        label="File path",
        description="",
        default_value=DEFAULT_SBML_PATH,
    )

    def _validate_file_path(self):
        file_extension = Path(self.file_path).suffix
        if file_extension not in [".xml", ".txt"]:
            raise ValueError(
                f"File path {self.file_path} does not end in either .xml or .txt"
            )

    def _load_definition(self):
        file_extension = Path(self.file_path).suffix

        definition = te.readFromFile(self.file_path)
        if file_extension == ".xml":
            definition = te.loadSBMLModel(definition).getAntimony()

        return definition

    def _get_species(self, definition):
        r = te.loadAntimonyModel(definition)
        species = r.getFloatingSpeciesAmountsNamedArray()

        return species.colnames

    def _get_spec_data(self, definition):
        return {"species": self._get_species(definition)}

    def configure(self, config_context: knext.ConfigurationContext):
        self._validate_file_path()

        definition = self._load_definition()
        spec_data = self._get_spec_data(definition)

        return ScrnDefinitionSpec(spec_data)

    def execute(self, exec_context: knext.ExecutionContext):
        definition = self._load_definition()
        spec_data = self._get_spec_data(definition)

        return ScrnDefinitionPortObject(ScrnDefinitionSpec(spec_data), definition)
