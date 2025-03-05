import sqlalchemy
import json
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator
from typing import Any

SIZE=256

class JSONType(TypeDecorator):
    impl = sqlalchemy.Text(SIZE)
    def process_bind_param(self, value: Any | None, dialect: sqlalchemy.Dialect) -> sqlalchemy.Any:
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value: Any | None, dialect: sqlalchemy.Dialect) -> Any | None:
        if value is not None:
            value = json.loads(value)
        return value

class Base(DeclarativeBase):
    ...

class Job(Base):
    __tablename__ = 'jobs'
    
    additionalInfo = sqlalchemy.Column(JSONType)
    brapiDataParameters = sqlalchemy.Column(JSONType)
    controlParameters = sqlalchemy.Column(JSONType)
    description = sqlalchemy.Column(sqlalchemy.String)
    externalReferences = sqlalchemy.Column(JSONType)
    fileDataParameters = sqlalchemy.Column(JSONType)
    jobCurrentStatus = sqlalchemy.Column(sqlalchemy.String)
    jobDbId = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    jobName = sqlalchemy.Column(sqlalchemy.String)
    jobOutput = sqlalchemy.Column(JSONType)
    jobOwnerName = sqlalchemy.Column(sqlalchemy.String)
    jobOwnerPersonDbId = sqlalchemy.Column(sqlalchemy.String)
    jobStatusMessages = sqlalchemy.Column(JSONType)
    procedureDbId = sqlalchemy.Column(sqlalchemy.String)

class Procedure(Base):
    __tablename__ = 'procedures'
    
    additionalInfo = sqlalchemy.Column(JSONType)
    brapiDataParameters = sqlalchemy.Column(JSONType)
    controlParameters = sqlalchemy.Column(JSONType)
    description = sqlalchemy.Column(sqlalchemy.String)
    documentationURL = sqlalchemy.Column(sqlalchemy.String)
    externalReferences = sqlalchemy.Column(JSONType)
    fileDataParameters = sqlalchemy.Column(JSONType)
    procedureDbId = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    procedureName = sqlalchemy.Column(sqlalchemy.String)
    
class Connector(Base):
    __tablename__ = 'connectors'
    
    procedureDbId = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    parameters = sqlalchemy.Column(JSONType)
    system = sqlalchemy.Column(sqlalchemy.String)