from pydantic import BaseModel
from enum import Enum

class DATA_TYPES(Enum):
    OBSERVATIONS = 'Observations'
    OBSERVATIONUNITS = 'ObservationUnits'
    GERMPLASM = 'Germplasm'
    SAMPLES = 'Samples'
    ALLELEMATRIX = 'AlleleMatrix'
    STUDIES = 'Studies'
    LOCATIONS = 'Locations'
    TRIALS = 'Trials'
    IMAGES = 'Images'
    LISTS = 'Lists'

class JOB_STATUS(Enum):
    SUBMITTED = 'SUBMITTED'
    QUEUED = 'QUEUED'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    ERRORED = 'ERRORED'
    CANCELED = 'CANCELED'

class BrAPIParameter(BaseModel):
    brapiParameterName: str|None = None
    brapiParameterType: str|None = None
    brapiParameterValue: str|None = None

class BrAPIDataParameter(BaseModel):
    authToken: str|None = None
    brapiBaseURL: str|None = None
    brapiParameters: list[BrAPIParameter]|None = None
    brapiVersions: list[str]|None = None
    dataType: str|None = None
    parameterId: str|None = None
    search: bool|None = None

class ControlParameter(BaseModel):
    parameterId: str|None = None
    parameterValue: str|None = None

class ExternalReference(BaseModel):
    referenceId: str|None = None
    referenceSource: str|None = None

class FileDataParameter(BaseModel):
    dataType: str|None = None
    fileSize: str|None = None
    fileTimeStamp: str|None = None
    fileURL: str|None = None
    mimeType: str|None = None
    parameterId: str|None = None

class JobOutput(BaseModel):
    dataType: str|None = None
    fileSize: str|None = None
    fileTimeStamp: str|None = None
    fileURL: str|None = None
    mimeType: str|None = None

class StatusMessage(BaseModel):
    message: str|None = None
    messageType: str|None = None
    timeStamp: str|None = None

class BaseJob(BaseModel):
    additionalInfo: dict|None = None
    brapiDataParameters: list[BrAPIDataParameter]|None = None
    controlParameters: list[ControlParameter]|None = None
    description: str|None = None
    externalReferences: list[ExternalReference]|None = None
    fileDataParameters: list[FileDataParameter]|None = None
    jobName: str|None = None
    jobOwnerName: str|None = None
    jobOwnerPersonDbId: str|None = None
    procedureDbId: str|None = None

class Job(BaseJob):
    jobCurrentStatus: str|None = None
    jobDbId: str
    jobOutput: list[JobOutput]|None = None
    jobStatusMessages: list[StatusMessage]|None = None
    