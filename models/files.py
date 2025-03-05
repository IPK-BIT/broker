from pydantic import BaseModel

class File(BaseModel):
    additionalInfo: dict|None = None
    fileURL: str
    fileName: str

class FileSearch(BaseModel):
    bucket: str
    fileURL: str
    encoding: str
    
class FileContent(BaseModel):
    data: str
    mimeType: str
    contentSize: int

class ArchiveRequest(BaseModel):
    bucket: str
    jobDbId: str