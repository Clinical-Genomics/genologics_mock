from urllib.parse import urlsplit, urlparse, parse_qs, urlunparse
from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional

import logging

logger = logging.getLogger(__name__)


class MockEntity(BaseModel):
    "Base class for the entities in the LIMS database."

    _TAG = None
    _URI = None
    _PREFIX = None


    def __init__(self, lims, id=None):

        if id in lims.enteties:
            self = lims.enteties[id]

        self.lims = lims
        self._id = id

    def put(self):
        """Save this instance in lims enteties."""
        self.lims.enteties[self._id] = self



class MockInstrument(MockEntity):
    """Lab Instrument
    """
    _URI = "instruments"
    _TAG = "instrument"
    _PREFIX = "inst"

    name: str
    type: str
    serial_number: str
    expiry_date: str
    archived: bool


class MockLab(MockEntity):
    "Lab; container of researchers."

    _URI = 'labs'
    _PREFIX = 'lab'

    name: str
    billing_address: Dict[str, str]
    shipping_address: Dict[str, str]
    udf: Dict[str, Optional]
    externalids: List[Tuple[str, str]]
    website: str


class MockResearcher(MockEntity):
    "Person; client scientist or lab personnel. Associated with a lab."

    _URI = 'researchers'
    _PREFIX = 'res'

    first_name: str
    last_name: str
    phone: str
    fax: str
    email: str
    initials: str
    lab: MockLab
    udf: Dict[str, Optional]
    externalids: List[Tuple[str, str]]
    username: str

    @property
    def name(self):
        return "%s %s" % (self.first_name, self.last_name)


class MockPermission(MockEntity):
    """A Clarity permission. Only supports GET"""
    name: str
    action: str
    description: str


class MockRole(MockEntity):
    """Clarity Role, hosting permissions"""
    name: str
    researchers: List[MockResearcher]
    permissions: List[MockPermission]


class MockReagent_label(MockEntity):
    """Reagent label element"""
    reagent_label: str


class MockNote(MockEntity):
    "Note attached to a project or a sample."

    content: str


class MockFile(MockEntity):
    "File attached to a project or a sample."

    attached_to: str
    content_location: str
    original_location: str
    is_published: bool


class MockProject(MockEntity):
    "Project concerning a number of samples; associated with a researcher."

    _URI = 'projects'
    _TAG = 'project'
    _PREFIX = 'prj'

    name: str
    open_date: str
    close_date: str
    invoice_date: str
    researcher: MockResearcher
    udf: Dict[str, Optional]
    files: List[MockFile]
    externalids: List[Tuple[str, str]]


class MockSample(MockEntity):
    "Customer's sample to be analyzed; associated with a project."

    _URI = 'samples'
    _TAG = 'sample'
    _PREFIX = 'smp'

    name: str
    date_received: str
    date_completed: str
    project: MockProject
    submitter: MockResearcher
    udf: Dict[str, Optional]
    notes: List[MockNote]
    files: List[MockFile]
    externalids: List[Tuple[str, str]]


class MockContainertype(MockEntity):
    "Type of container for analyte artifacts."

    _TAG = 'container-type'
    _URI = 'containertypes'
    _PREFIX = 'ctp'

    name: str
    calibrant_wells: List[str]
    unavailable_wells: List[str]
    x_dimension: Dict[str, Optional]
    y_dimension: Dict[str, Optional]


class MockContainer(MockEntity):
    "Container for analyte artifacts."

    _URI = 'containers'
    _TAG = 'container'
    _PREFIX = 'con'

    name: str
    type: MockContainertype
    occupied_wells: int
    placements: Dict[str, MockArtifact]
    udf: Dict[str, Optional]
    state: str

    def get_placements(self):
        """Get the dictionary of locations and artifacts
        using the more efficient batch call."""
        result = self.placements.copy()
        self.lims.get_batch(list(result.values()))
        return result

    def delete(self):
        self.lims.delete(self.uri)


class MockUdfconfig(MockEntity):
    "Instance of field type (cnf namespace)."
    _URI = 'configuration/udfs'

    name: str
    attach_to_name: str
    attach_to_category: str
    show_in_lablink: bool
    allow_non_preset_values: bool
    first_preset_is_default_value: bool
    show_in_tables: bool
    is_editable: bool
    is_required: bool
    is_deviation: bool
    is_controlled_vocabulary: bool
    presets: List[str]


class MockProcesstype(MockEntity):
    _TAG = 'process-type'
    _URI = 'processtypes'
    _PREFIX = 'ptp'

    def __init__(self, lims, uri=None, id=None, _create_new=False):
        super(MockProcesstype, self).__init__(lims, uri, id, _create_new)

    name: str
    field_definition: List[MockUdfconfig]
    process_inputs: Optional  ## figure this out!!!
    process_outputs: Optional  ## figure this out!!!
    process_type_attribute = Dict[str, str]

    @property
    def process_input(self):
        return self.process_inputs[0]


class MockControlType(MockEntity):
    _URI = "controltypes"
    _TAG = "control-type"
    _PREFIX = 'ctrltp'

    name: str
    supplier: str
    archived: bool
    single_step: bool


class MockProcess(MockEntity):
    "Process (instance of Processtype) executed producing ouputs from inputs."

    _URI = 'processes'
    _PREFIX = 'prc'

    type: MockProcesstype
    date_run: str
    technician: MockResearcher
    protocol_name: str
    input_output_maps: List[Tuple[Dict[str, str], Dict[str, str]]]
    udf: Dict[str, Optional]
    files: List[MockFile]
    process_parameter: str
    instrument: MockInstrument

    def outputs_per_input(self, inart, ResultFile=False, SharedResultFile=False, Analyte=False):
        """Getting all the output artifacts related to a particual input artifact"""

        inouts = [io for io in self.input_output_maps if io[0]['limsid'] == inart]
        if ResultFile:
            inouts = [io for io in inouts if io[1]['output-type'] == 'ResultFile']
        elif SharedResultFile:
            inouts = [io for io in inouts if io[1]['output-type'] == 'SharedResultFile']
        elif Analyte:
            inouts = [io for io in inouts if io[1]['output-type'] == 'Analyte']
        outs = [io[1]['uri'] for io in inouts]
        return outs

    def input_per_sample(self, sample):
        """gettiung all the input artifacts dereved from the specifyed sample"""
        ins_all = self.all_inputs()
        ins = []
        for inp in ins_all:
            for samp in inp.samples:
                if samp.name == sample and inp not in ins:
                    ins.append(inp)
        return ins

    def all_inputs(self, unique=True, resolve=False):
        """Retrieving all input artifacts from input_output_maps
        if unique is true, no duplicates are returned.
        """
        # if the process has no input, that is not standard and we want to know about it
        try:
            ids = [io[0]['limsid'] for io in self.input_output_maps]
        except TypeError:
            logger.error("Process ", self, " has no input artifacts")
            raise TypeError
        if unique:
            ids = list(frozenset(ids))
        if resolve:
            return self.lims.get_batch([MockArtifact(self.lims, id=id) for id in ids if id is not None])
        else:
            return [MockArtifact(self.lims, id=id) for id in ids if id is not None]

    def all_outputs(self, unique=True, resolve=False):
        """Retrieving all output artifacts from input_output_maps
        if unique is true, no duplicates are returned.
        """
        # Given how ids is structured, io[1] might be None : some process don't have an output.
        ids = [io[1]['limsid'] for io in self.input_output_maps if io[1] is not None]
        if unique:
            ids = list(frozenset(ids))
        if resolve:
            return self.lims.get_batch([MockArtifact(self.lims, id=id) for id in ids if id is not None])
        else:
            return [MockArtifact(self.lims, id=id) for id in ids if id is not None]

    def shared_result_files(self):
        """Retreve all resultfiles of output-generation-type PerAllInputs."""
        artifacts = self.all_outputs(unique=True)
        return [a for a in artifacts if a.output_type == 'SharedResultFile']

    def result_files(self):
        """Retreve all resultfiles of output-generation-type perInput."""
        artifacts = self.all_outputs(unique=True)
        return [a for a in artifacts if a.output_type == 'ResultFile']

    def analytes(self):
        """Retreving the output Analytes of the process, if existing.
        If the process is not producing any output analytes, the input
        analytes are returned. Input/Output is returned as a information string.
        Makes aggregate processes and normal processes look the same."""
        info = 'Output'
        artifacts = self.all_outputs(unique=True)
        analytes = [a for a in artifacts if a.type == 'Analyte']
        if len(analytes) == 0:
            artifacts = self.all_inputs(unique=True)
            analytes = [a for a in artifacts if a.type == 'Analyte']
            info = 'Input'
        return analytes, info

    def parent_processes(self):
        """Retrieving all parent processes through the input artifacts"""
        return [i_a.parent_process for i_a in self.all_inputs(unique=True)]

    def output_containers(self):
        """Retrieve all unique output containers"""
        cs = []
        for o_a in self.all_outputs(unique=True):
            if o_a.container:
                cs.append(o_a.container)
        return list(frozenset(cs))

    @property
    def step(self):
        """Retrive the Step coresponding to this process. They share the same id"""
        return MockStep(self.lims, id=self.id)


class MockArtifact(MockEntity):
    "Any process input or output; analyte or file."

    _URI = 'artifacts'
    _TAG = 'artifact'
    _PREFIX = 'art'

    name: str
    type: str
    output_type: str
    parent_process: MockProcess
    volume: str
    concentration: str
    qc_flag: str
    location: MockContainer
    working_flag: bool
    samples: List[MockSample]
    udf: Dict[str, Optional]
    files: List[MockFile]
    reagent_labels: List[str]


    def input_artifact_list(self):
        """Returns the input artifact ids of the parrent process."""
        input_artifact_list = []
        try:
            for tuple in self.parent_process.input_output_maps:
                if tuple[1]['limsid'] == self.id:
                    input_artifact_list.append(tuple[0]['uri'])  # ['limsid'])
        except:
            pass
        return input_artifact_list

    def get_state(self):
        "Parse out the state value from the URI."
        parts = urlparse(self.uri)
        params = parse_qs(parts.query)
        try:
            return params['state'][0]
        except (KeyError, IndexError):
            return None

    @property
    def container(self):
        "The container where the artifact is located, or None"
        try:
            return self.location[0]
        except:
            return None

    def stateless(self):
        "returns the artefact independently of it's state"
        parts = urlparse(self.uri)
        if 'state' in parts[4]:
            stateless_uri = urlunparse([parts[0], parts[1], parts[2], parts[3], '', ''])
            return MockArtifact(self.lims, uri=stateless_uri)
        else:
            return self

    state = property(get_state)
    stateless = property(stateless)

    def _get_workflow_stages_and_statuses(self):
        self.get()
        result = []
        rootnode = self.root.find('workflow-stages')
        for node in rootnode.findall('workflow-stage'):
            result.append((MockStage(self.lims, uri=node.attrib['uri']), node.attrib['status'], node.attrib['name']))
        return result

    workflow_stages_and_statuses = property(_get_workflow_stages_and_statuses)


class MockStepProgramStatus(MockEntity):
    """Allows custom handling of program status.
    message supports HTML. Cross handling of EPPs is possible.
    Supports PUT"""
    status: str
    message: str


class MockReagentKit(MockEntity):
    """Type of Reagent with information about the provider"""
    _URI = "reagentkits"
    _TAG = "reagent-kit"
    _PREFIX = 'kit'

    name: str
    supplier: str
    website: str
    archived: bool


class MockReagentLot(MockEntity):
    """Reagent Lots contain information about a particualr lot of reagent used in a step"""
    _URI = "reagentlots"
    _TAG = "reagent-lot"
    _PREFIX = 'lot'

    reagent_kit: MockReagentKit
    name: str
    lot_number: str
    created_date: str
    last_modified_date: str
    expiry_date: str
    created_by: MockResearcher
    last_modified_by: MockResearcher
    status: str
    usage_count: int


class MockStepReagentLots(MockEntity):
    reagent_lots: List[MockReagentLot]


class MockStepDetails(MockEntity):
    """Detail associated with a step"""

    input_output_maps: List[Tuple[Dict[str, str], Dict[str, str]]]
    udf: Dict[str, Optional]


class MockStepReagents(MockEntity):
    reagent_category: str
    output_reagents: Dict[MockArtifact, str]


class MockStep(MockEntity):
    "Step, as defined by the genologics API."

    _URI = 'steps'
    _PREFIX = 'stp'

    current_state: str
    _reagent_lots: MockStepReagentLots
    # placements: MockStepPlacements Handle this!!"
    details: MockStepDetails
    program_status: MockStepProgramStatus
    reagents: MockStepReagents

    @property
    def reagent_lots(self):
        return self._reagent_lots.reagent_lots


class MockProtocolStep(MockEntity):
    """Steps key in the Protocol object"""

    _TAG = 'step'

    name: str
    type: MockProcesstype
    permittedcontainers: List[str]
    permitted_control_types: List[MockControlType]
    required_reagent_kits: List[MockReagentKit]
    queue_fields: List[Dict[str, Optional]]
    step_fields: List[Dict[str, Optional]]
    sample_fields: List[Dict[str, Optional]]
    step_properties: List[Dict[str, Optional]]
    epp_triggers: List[Dict[str, Optional]]


class MockProtocol(MockEntity):
    """Protocol, holding ProtocolSteps and protocol-properties"""
    _URI = 'configuration/protocols'
    _TAG = 'protocol'

    steps: List[MockProtocolStep]
    properties: List[Dict[str, Optional]]


class MockAutomation(MockEntity):
    """Automation, holding Automation configurations"""
    _URI = 'configuration/automations'
    _TAG = 'automation'

    process_types: List[MockProcesstype]
    string: str
    name: str
    context: str


class MockStage(MockEntity):
    """Holds Protocol/Workflow"""
    name: str
    index: int
    protocol: MockProtocol
    step: MockProtocolStep


class MockWorkflow(MockEntity):
    """ Workflow, introduced in 3.5"""
    _URI = "configuration/workflows"
    _TAG = "workflow"

    name: str
    status: str
    protocols: List[MockProtocol]
    stages: List[MockStage]


class MockReagentType(MockEntity):
    """Reagent Type, usually, indexes for sequencing"""
    _URI = "reagenttypes"
    _TAG = "reagent-type"
    _PREFIX = 'rtp'

    category: str
    name: str

    def __init__(self, lims, uri=None, id=None):
        super(MockReagentType, self).__init__(lims, uri, id)
        assert self.uri is not None
        self.root = lims.get(self.uri)
        self.sequence = None
        for t in self.root.findall('special-type'):
            if t.attrib.get("name") == "Index":
                for child in t.findall("attribute"):
                    if child.attrib.get("name") == "Sequence":
                        self.sequence = child.attrib.get("value")


MockSample.artifact = MockArtifact
MockStage.workflow = MockWorkflow
MockArtifact.workflow_stages = List[MockStage]
MockStep.configuration = MockProtocolStep
MockStepProgramStatus.configuration = MockProtocolStep
MockResearcher.roles = List[MockRole]
