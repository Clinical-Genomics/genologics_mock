from typing import List


class MockProcessType:
    def __init__(self, name=""):
        self.name = name

    def __repr__(self):
        return f"ProcessType:name={self.name}"


class MockContainerType:
    def __init__(self, name=""):
        self.name = name

    def __repr__(self):
        return f"ProcessType:name={self.name}"


class MockContainer:
    def __init__(self, name="", type=MockContainerType()):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"ProcessType:name={self.name}"


class MockArtifact:
    def __init__(
        self,
        parent_process=None,
        samples=None,
        id=None,
        location=(),
        udf={},
        qc_flag="UNKNOWN",
        reagent_labels=[],
        type=None,
    ):
        self.id = id
        self.location = location
        self.parent_process = parent_process
        self.samples = samples
        self.input_list = []
        self.udf = udf
        self.qc_flag = qc_flag
        self.reagent_labels = reagent_labels
        self.type = type

    def input_artifact_list(self):
        return self.input_list

    def put(self):
        pass

    def __repr__(self):
        return f"Artifact:parent_process={self.parent_process},samples={self.samples}"


class MockSample:
    def __init__(self, sample_id="sample", udfs={}, artifact=MockArtifact()):
        self.id = sample_id
        self.udf = udfs
        self.artifact = artifact

    def __repr__(self):
        return f"Sample:id={self.id},udf={self.udf}"


class MockReagentLabel:
    def __init__(
        self,
        name="IDT_10nt_NXT_109",
        sequence="TAGGAAGCGG-CCTGGATTGG",
        category="Illumina IDT",
    ):
        self.name = name
        self.sequence = sequence
        self.category = category

    def __repr__(self):
        return f"ReagentLabel:name={self.name},category={self.category}"


class MockProcess:
    def __init__(
        self,
        date_run: str = "2018-01-01",
        process_type: MockProcessType = None,
        udf: dict = {},
        input_artifact_list: List[MockArtifact] = [],
        pid: str = None,
        outputs: List[MockArtifact]=[],
        input_output_maps: list = [],
    ):
        self.date_run = date_run
        self.type = process_type
        self.udf = udf
        self.input_artifact_list = input_artifact_list
        self.id = pid
        self.outputs = outputs
        self.input_output_maps = input_output_maps

    def all_outputs(self, unique=False):

        if unique:
            return list(set(self.outputs))
        return self.outputs

    def all_inputs(self, unique=False):

        if unique:
            return list(set(self.input_artifact_list))
        return self.input_artifact_list

    def __repr__(self):
        return f"Process:date_run={self.date_run},type={self.type}"
