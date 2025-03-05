import requests
from icecream import ic
import os
from uuid import uuid4
from litestar import Controller, get, post, Response
from litestar.background_tasks import BackgroundTask
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.jobs import BaseJob, Job
from models.responses import Response as BrAPIResponse, SingleResponse, Metadata, Pagination, Message, Result, MESSAGETYPE
from db.models import Connector, Job as DbJob
from connectors import clowm, divassociate


class JobController(Controller):
    path = "/jobs"
    jobDbId = ''
    
    @get('/')
    async def get_all_jobs(self, transaction: AsyncSession, jobOwnerPersonDbId: str|None = None) -> Response[Job]:
        print('Getting Jobs')
        query = select(DbJob)
        if jobOwnerPersonDbId:
            query = query.where(DbJob.jobOwnerPersonDbId == jobOwnerPersonDbId)
            
        print('Query: ', query)
        
        db_jobs = (await transaction.execute(query)).scalars().all()
        
        print('Jobs: ', db_jobs)
        jobs = []
        for db_job in db_jobs:
            db_connector = (await transaction.execute(select(Connector).where(Connector.procedureDbId == db_job.procedureDbId))).scalar()
                    
            if db_connector.system == 'CLOWM':
                if (db_job.jobCurrentStatus!='SUCCESS' and db_job.jobCurrentStatus!='ERROR'):
                    response = await clowm.get_job_status(db_job)
                    print('Response: ', response)
                    db_job.jobCurrentStatus = response['status']
                transaction.add(db_job)

            job = Job(**db_job.__dict__)
            jobs.append(job)

        return Response(BrAPIResponse(
            metadata=Metadata(
                pagination=Pagination(
                    currentPage=0,
                    pageSize=1000,
                    totalCount=len(jobs),
                    totalPages=1
                ),
                datafiles=[],
                status=[
                    Message(
                        message="Jobs retrieved successfully",
                        messageType=MESSAGETYPE.INFO
                    )
                ]
            ),
            result=Result(
                data=jobs,
            )
        ))
    
    @post('/')
    async def create_jobs(self, transaction: AsyncSession, data: BaseJob) -> Response[Job]:
        ic('Creating Job')
        ic('Procedure ID: ', data.procedureDbId)
        stmnt = select(Connector).where(Connector.procedureDbId == data.procedureDbId)
        ic('Statement: ',stmnt)
        connector = (await transaction.execute(stmnt)).scalar()
        ic('Connector Found for: ', connector.system)
        
        job = Job(**data.model_dump(), jobDbId=str(uuid4()))
        ic(f'Job Created with ID: {job.jobDbId}')
        
        if data.procedureDbId=='01920019-f7a1-767e-ae0e-4b3ba1f064cb':
            divassociate.transform_data(job, connector)
        ic('Transformed Data')

        if connector.system == 'CLOWM':
            await clowm.submit_data(job.jobDbId, job.additionalInfo['s3Bucket'])
            ic('Data Submitted to CLOWM')
            response = await clowm.submit_job(job, "b5fc09af887d4d642a113931549b5eaf0e9fb097")
            ic('Job Submitted to CLOWM')
            job.additionalInfo['execution_id']=response['execution_id']
            job.jobCurrentStatus=response['status']
            db_job = DbJob(**job.model_dump())
            transaction.add(db_job)
            await transaction.commit()
            ic('Job Committed to Database')
            job.jobCurrentStatus='Submitted'
        if data.procedureDbId=='01920019-f7a1-767e-ae0e-4b3ba1f064cb':
            os.remove(f'{job.jobDbId}/germplasm.tsv')
            os.remove(f'{job.jobDbId}/observations.tsv')
            os.removedirs(job.jobDbId)
            ic('Files Removed')
        
        return Response(BrAPIResponse(
            metadata=Metadata(
                pagination=Pagination(
                    totalCount=1
                ),
                datafiles=[],
                status=[
                    Message(
                        message="Job created successfully",
                        messageType=MESSAGETYPE.INFO
                    )
                ]
            ),
            result=Result(
                data=[job],
            )
        ))#, background=BackgroundTask(logging_task, 'test', f'{jobDbId}'))
    
    @get('/{jobDbId: str}')
    async def get_job(self, transaction:AsyncSession, jobDbId: str) -> SingleResponse[Job]:
        db_job = (await transaction.execute(select(DbJob).where(DbJob.jobDbId == jobDbId))).scalar()
        db_connector = (await transaction.execute(select(Connector).where(Connector.procedureDbId == db_job.procedureDbId))).scalar()
        
        if db_connector.system == 'CLOWM':
            response = await clowm.get_job_status(db_job)
            db_job.jobCurrentStatus = response['status']
            transaction.add(db_job)

        job = Job(**db_job.__dict__)

        return SingleResponse(
            metadata=Metadata(
                pagination=Pagination(
                    currentPage=0,
                    pageSize=1000,
                    totalCount=1,
                    totalPages=1
                ),
                datafiles=[],
                status=[
                    Message(
                        message="Job retrieved successfully",
                        messageType=MESSAGETYPE.INFO
                    )
                ]
            ),
            result=job,
        )