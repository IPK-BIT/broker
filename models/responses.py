from pydantic import BaseModel
from typing import TypeVar, Generic
from enum import Enum

T = TypeVar('T')

class MESSAGETYPE(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    
class DataFile(BaseModel):
    fileDescription: str|None = None
    fileMD5Hash: str|None = None
    fileName: str|None = None
    fileSize: int|None = None
    fileType: str|None = None
    fileURL: str|None = None

class Message(BaseModel):
    message: str|None = None
    messageType: MESSAGETYPE|None = None

class Pagination(BaseModel):
    currentPage: int|None = None
    pageSize: int|None = None
    totalCount: int|None = None
    totalPages: int|None = None

class Metadata(BaseModel):
    pagination: Pagination
    status: list[Message]
    datafiles: list[DataFile]
    
class Result(BaseModel, Generic[T]):
    data: list[T]

class Response(BaseModel, Generic[T]):
    metadata: Metadata
    result: Result[T]    
    
class SingleResponse(BaseModel, Generic[T]):
    metadata: Metadata
    result: T