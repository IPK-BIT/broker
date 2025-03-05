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

class BrAPIDataParameter(BaseModel):
    alternateParameters: list[str]|None = None
    dataType: str|None = None
    parameterId: str|None = None
    parameterName: str|None = None
    required: bool|None = None

class ControlParameter(BaseModel):
    dataType: str|None = None
    defaultValue: str|None = None
    exampleValue: str|None = None
    parameterId: str|None = None
    parameterName: str|None = None
    required: bool|None = None
    
class ExternalReference(BaseModel):
    referenceId: str|None = None
    referenceSource: str|None = None
    
class FileDataParameter(BaseModel):
    alternativeParameters: list[str]|None = None
    dataTypes: list[str]|None = None
    mimeTypes: list[str]|None = None
    parameterId: str|None = None
    parameterName: str|None = None
    required: bool|None = None

class BaseProcedure(BaseModel):
    additionalInfo: dict|None = None
    brapiDataParameters: list[BrAPIDataParameter]|None = None
    controlParameters: list[ControlParameter]|None = None
    description: str|None = None
    documentationURL: str|None = None
    externalReferences: list[ExternalReference]|None = None
    fileDataParameters: list[FileDataParameter]|None = None
    procedureName: str|None = None
    
class Procedure(BaseProcedure):
    procedureDbId: str