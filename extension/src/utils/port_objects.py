"""
Contains definitions of custom node port objects:
- SCRN definition
- Simulation data
- Deep Abstraction model
"""
import knime.extension as knext
import pickle


##### SCRN Definition #####
class ScrnDefinitionSpec(knext.PortObjectSpec):
    def __init__(self, spec_data: str) -> None:
        self._spec_data = spec_data

    def serialize(self) -> dict:
        return {"spec_data": self._spec_data}

    @classmethod
    def deserialize(cls, data: dict) -> "ScrnDefinitionSpec":
        return cls(data["spec_data"])

    @property
    def spec_data(self):
        return self._spec_data


class ScrnDefinitionPortObject(knext.PortObject):
    def __init__(self, spec: ScrnDefinitionSpec, data) -> None:
        super().__init__(spec)
        self._data = data
        self._spec = spec

    def serialize(self):
        return pickle.dumps(self._data)

    @classmethod
    def deserialize(
        cls, spec: ScrnDefinitionSpec, data: bytes
    ) -> "ScrnDefinitionPortObject":
        return cls(spec, pickle.loads(data))

    @property
    def data(self):
        return self._data

    @property
    def spec(self):
        return self._spec


scrn_definition_port_type = knext.port_type(
    name="SCRN Definition",
    object_class=ScrnDefinitionPortObject,
    spec_class=ScrnDefinitionSpec,
)
