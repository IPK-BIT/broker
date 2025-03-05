import uuid
from litestar import Controller, get, post
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.procedures import BaseProcedure, Procedure
from models.responses import Response, SingleResponse, Metadata, Pagination, Message, Result, MESSAGETYPE
from db.models import Procedure as DbProcedure
from math import ceil

class ProcedureController(Controller):
    path = "procedures"
    
    @get('/')
    async def get_all_procedures(self, transaction: AsyncSession) -> Response[Procedure]:
        stmnt = select(DbProcedure)
        db_results = (await transaction.execute(stmnt)).scalars().all()
        result = []
        for db_result in db_results:
            result.append(Procedure(**db_result.__dict__))
        return Response(
            metadata=Metadata(
                datafiles=[],
                pagination=Pagination(
                    currentPage=0,
                    pageSize=1000,
                    totalCount=len(result),
                    totalPages=ceil(len(result)/1000)
                ),
                status=[
                    Message(
                        message="Success",
                        messageType=MESSAGETYPE.INFO
                    )
                ]
            ),
            result=Result(data=result)
        )
    
    @post('/', description="Register a new procedure. Not documented in Specs.")
    async def register_procedures(self, transaction: AsyncSession, data: BaseProcedure) -> Response[Procedure]:
        if isinstance(data, list):
            for item in data:
                db_procedure = DbProcedure(**item, procedureDbId=str(uuid.uuid4()))
                transaction.add(db_procedure)
        else:
            db_procedure = DbProcedure(**data.model_dump(), procedureDbId = str(uuid.uuid4()))
            transaction.add(db_procedure)
        return Response(
            metadata=Metadata(
                datafiles=[],
                pagination=Pagination(
                    currentPage=0,
                    pageSize=1,
                    totalCount=1,
                    totalPages=1
                ),
                status=[
                    Message(
                        message="Success",
                        messageType=MESSAGETYPE.INFO
                    )
                ]
            ),
            result=Result(data=[data])
        )
    
    @get('/{procedureDbId: str}')
    async def get_procedure(self, transaction: AsyncSession, procedureDbId: str) -> SingleResponse[Procedure]:
        stmnt = select(DbProcedure).where(DbProcedure.procedureDbId == procedureDbId)
        db_result = (await transaction.execute(stmnt)).scalar()
        if db_result:
            return SingleResponse(
                metadata=Metadata(
                    datafiles=[],
                    pagination=Pagination(
                        currentPage=0,
                        pageSize=1,
                        totalCount=1,
                        totalPages=1
                    ),
                    status=[
                        Message(
                            message="Success",
                            messageType=MESSAGETYPE.INFO
                        )
                    ]
                ),
                result=Procedure(**db_result.__dict__)
            )
        else:                
            return SingleResponse(
                metadata=Metadata(
                    datafiles=[],
                    pagination=Pagination(
                        currentPage=0,
                        pageSize=1,
                        totalCount=0,
                        totalPages=1
                    ),
                    status=[
                        Message(
                            message="No procedure found with the given ID",
                            messageType=MESSAGETYPE.INFO
                        )
                    ]
                ),
                result=None
            )