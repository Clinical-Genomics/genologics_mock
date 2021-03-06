from genologics_mock.entities import MockArtifact, MockProcess, MockProcessType, MockSample
import logging
LOG = logging.getLogger(__name__)


class MockLims():
    def __init__(self):
        self.artifacts = []
        self.processes = []
        self.process_types = []
        self.samples = []

    def get_samples(self) -> list:
        return self.samples

    def get_artifacts(self, process_type: list, samplelimsid: str, type: str) -> list:
        """"Get a list of artifacts."""

        if not isinstance(process_type, list):
            process_type = [process_type]

        arts = []

        for art in self.artifacts:
            if type:
                if not art.type==type:
                    continue
            if process_type:
                if not art.parent_process:
                    continue
                elif not art.parent_process.type.name in process_type:
                    continue
            if samplelimsid:
                if not samplelimsid in [s.id for s in art.samples]:
                    continue
            arts.append(art)

        return arts

    def get_processes(self, type=None, udf={}, inputartifactlimsid=None, last_modified=None):
        processes = []
        for process in self.processes:
            if isinstance(type, list) and (process.type.name not in type):
                continue
            elif isinstance(type, str) and (process.type.name != type):
                continue
            if udf:
                subset = {key: process.udf.get(key) for key in udf}
                if subset != udf:
                    continue
            if inputartifactlimsid:
                if inputartifactlimsid not in [
                    a.id for a in process.input_artifact_list
                ]:
                    continue
            if last_modified:
                LOG.info(process.modified)
                if last_modified > process.modified:
                    continue
            processes.append(process)
        LOG.info(str(processes))
        return processes

    def __repr__(self):
        return (f"Lims:artifacts={self.artifacts},process={self.processes},"
                "process_types={self.process_types},samples={self.samples}")
