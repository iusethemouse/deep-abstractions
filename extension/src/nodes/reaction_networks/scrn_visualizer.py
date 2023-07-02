import knime.extension as knext
import tellurium as te
import SBMLDiagrams as sd
from PIL import Image
import tempfile
import os
import io

from utils.port_objects import (
    scrn_definition_port_type,
    ScrnDefinitionSpec,
    ScrnDefinitionPortObject,
)

from utils.categories import reaction_networks_category


@knext.node(
    name="SCRN Visualizer",
    node_type=knext.NodeType.VISUALIZER,
    icon_path="src/assets/icons/icon.png",
    category=reaction_networks_category,
)
@knext.input_port(
    name="SCRN Definition",
    description="",
    port_type=scrn_definition_port_type,
)
@knext.output_view(name="Network diagram", description="")
class ScrnVisualizer:
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

        temp_file = tempfile.mkstemp(suffix=".png")[1]
        buffer = io.BytesIO()

        r = te.loadAntimonyModel(definition)
        diagram = sd.load(r.getSBML())
        diagram.draw(setImageSize=[600, 300], output_fileName=temp_file)

        img = Image.open(temp_file)
        img.save(buffer, format="PNG")

        os.remove(temp_file)

        return knext.view_png(buffer.getvalue())
