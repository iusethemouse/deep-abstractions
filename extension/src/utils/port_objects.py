"""
Contains definitions of custom node port objects:
- SRN definition
- Simulation data
- Deep Abstraction model
"""
import knime.extension as knext
import pickle


########## SRN DEFINITION ##########
class SrnDefinitionSpec(knext.PortObjectSpec):
    def __init__(self, spec_data: str) -> None:
        self._spec_data = spec_data

    def serialize(self) -> dict:
        return {"spec_data": self._spec_data}

    @classmethod
    def deserialize(cls, data: dict) -> "SrnDefinitionSpec":
        return cls(data["spec_data"])

    @property
    def spec_data(self):
        return self._spec_data


class SrnDefinitionPortObject(knext.PortObject):
    def __init__(self, spec: SrnDefinitionSpec, data) -> None:
        super().__init__(spec)
        self._data = data
        self._spec = spec

    def serialize(self):
        return pickle.dumps(self._data)

    @classmethod
    def deserialize(
        cls, spec: SrnDefinitionSpec, data: bytes
    ) -> "SrnDefinitionPortObject":
        return cls(spec, pickle.loads(data))

    @property
    def data(self):
        return self._data

    @property
    def spec(self):
        return self._spec


srn_definition_port_type = knext.port_type(
    name="SRN Definition",
    object_class=SrnDefinitionPortObject,
    spec_class=SrnDefinitionSpec,
)


########## SIMULATION DATA ##########
class SimulationDataSpec(knext.PortObjectSpec):
    def __init__(self, spec_data: str) -> None:
        self._spec_data = spec_data

    def serialize(self) -> dict:
        return {"spec_data": self._spec_data}

    @classmethod
    def deserialize(cls, data: dict) -> "SimulationDataSpec":
        return cls(data["spec_data"])

    @property
    def spec_data(self):
        return self._spec_data


class SimulationDataPortObject(knext.PortObject):
    def __init__(self, spec: SimulationDataSpec, data) -> None:
        super().__init__(spec)
        self._data = data
        self._spec = spec

    def serialize(self):
        return pickle.dumps(self._data)

    @classmethod
    def deserialize(
        cls, spec: SimulationDataSpec, data: bytes
    ) -> "SimulationDataPortObject":
        return cls(spec, pickle.loads(data))

    @property
    def data(self):
        return self._data

    @property
    def spec(self):
        return self._spec


simulation_data_port_type = knext.port_type(
    name="Simulation Data",
    object_class=SimulationDataPortObject,
    spec_class=SimulationDataSpec,
)
