import knime.extension as knext
import tellurium as te
from pathlib import Path

from utils.port_objects import (
    srn_definition_port_type,
    SrnDefinitionSpec,
    SrnDefinitionPortObject,
)

from utils.categories import reaction_networks_category

DEFAULT_WRITE_PATH = "/Users/ivan/Downloads/tmp/"
DEFAULT_FILENAME = "srn"


@knext.node(
    name="SRN Writer",
    node_type=knext.NodeType.SINK,
    icon_path="src/assets/icons/icon.png",
    category=reaction_networks_category,
)
@knext.input_port(
    name="SRN Definition",
    description="",
    port_type=srn_definition_port_type,
)
class SrnWriter:
    class AvailableFormats(knext.EnumParameterOptions):
        SBML = ("SBML", "Write to an `.xml` file in the SBML format (standard).")
        ANTIMONY = (
            "Antimony",
            "Write to a `.txt` file in the Antimony format (human-readable).",
        )

    format_selection = knext.EnumParameter(
        label="Output format",
        description="",
        default_value=AvailableFormats.SBML.name,
        enum=AvailableFormats,
    )

    filename = knext.StringParameter(
        label="Output filename", description="", default_value=DEFAULT_FILENAME
    )

    destination = knext.StringParameter(
        label="Output directory",
        description="",
        default_value=DEFAULT_WRITE_PATH,
    )

    def configure(
        self, config_context: knext.ConfigurationContext, input_spec: SrnDefinitionSpec
    ):
        return

    def execute(
        self,
        exec_context: knext.ExecutionContext,
        input_port_object: SrnDefinitionPortObject,
    ):
        definition = input_port_object.data
        extension = ".txt"

        if self.format_selection == self.AvailableFormats.SBML.name:
            definition = te.antimonyToSBML(definition)
            extension = ".xml"

        directory = Path(self.destination).joinpath(self.filename + extension)

        with open(directory, "w") as f:
            f.write(definition)

        return