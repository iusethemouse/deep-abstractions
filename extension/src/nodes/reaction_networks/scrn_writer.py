import knime.extension as knext
import tellurium as te

from utils.port_objects import (
    scrn_definition_port_type,
    ScrnDefinitionSpec,
    ScrnDefinitionPortObject,
)

from utils.categories import reaction_networks_category

DEFAULT_WRITE_PATH = "/Users/ivan/Downloads/tmp/my_srn.xml"


@knext.node(
    name="SCRN Writer",
    node_type=knext.NodeType.SINK,
    icon_path="src/assets/icons/icon.png",
    category=reaction_networks_category,
)
@knext.input_port(
    name="SCRN Definition",
    description="",
    port_type=scrn_definition_port_type,
)
class ScrnWriter:
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

    file_path = knext.StringParameter(
        label="File path",
        description="",
        default_value=DEFAULT_WRITE_PATH,
    )

    def configure(
        self, config_context: knext.ConfigurationContext, input_spec: ScrnDefinitionSpec
    ):
        return

    def execute(
        self,
        exec_context: knext.ExecutionContext,
        input_port_object: ScrnDefinitionPortObject,
    ):
        definition = input_port_object.data

        if self.format_selection == self.AvailableFormats.SBML.name:
            definition = te.antimonyToSBML(definition)

        with open(self.file_path, "w") as f:
            f.write(definition)

        return
