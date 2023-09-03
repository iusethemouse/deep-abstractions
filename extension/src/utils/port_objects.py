"""
Contains definitions of custom node port objects:
- CRN definition
- Training simulation data
- Deep Abstraction model
"""
import knime.extension as knext
import pickle


########## CRN DEFINITION ##########
class CrnDefinitionSpec(knext.PortObjectSpec):
    def __init__(self, spec_data: str) -> None:
        self._spec_data = spec_data

    def serialize(self) -> dict:
        return {"spec_data": self._spec_data}

    @classmethod
    def deserialize(cls, data: dict) -> "CrnDefinitionSpec":
        return cls(data["spec_data"])

    @property
    def spec_data(self):
        return self._spec_data


class CrnDefinitionPortObject(knext.PortObject):
    def __init__(self, spec: CrnDefinitionSpec, data) -> None:
        super().__init__(spec)
        self._data = data
        self._spec = spec

    def serialize(self):
        return pickle.dumps(self._data)

    @classmethod
    def deserialize(
        cls, spec: CrnDefinitionSpec, data: bytes
    ) -> "CrnDefinitionPortObject":
        return cls(spec, pickle.loads(data))

    @property
    def data(self):
        return self._data

    @property
    def spec(self):
        return self._spec


crn_definition_port_type = knext.port_type(
    name="CRN Definition",
    object_class=CrnDefinitionPortObject,
    spec_class=CrnDefinitionSpec,
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


########## DEEP ABSTRACTION MODEL ##########
class DeepAbstractionModelSpec(knext.PortObjectSpec):
    def __init__(self, spec_data: str) -> None:
        self._spec_data = spec_data

    def serialize(self) -> dict:
        return {"spec_data": self._spec_data}

    @classmethod
    def deserialize(cls, data: dict) -> "DeepAbstractionModelSpec":
        return cls(data["spec_data"])

    @property
    def spec_data(self):
        return self._spec_data


class DeepAbstractionModelPortObject(knext.PortObject):
    def __init__(self, spec: DeepAbstractionModelSpec, data) -> None:
        super().__init__(spec)
        self._data = data
        self._spec = spec

    def serialize(self):
        return pickle.dumps(self._data)

    @classmethod
    def deserialize(
        cls, spec: DeepAbstractionModelSpec, data: bytes
    ) -> "DeepAbstractionModelPortObject":
        return cls(spec, pickle.loads(data))

    @property
    def data(self):
        return self._data

    @property
    def spec(self):
        return self._spec


deep_abstraction_model_port_type = knext.port_type(
    name="Deep Abstraction Model",
    object_class=DeepAbstractionModelPortObject,
    spec_class=DeepAbstractionModelSpec,
)
