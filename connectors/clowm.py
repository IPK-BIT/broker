import zipfile
import tempfile
import base64
from icecream import ic
import os
import requests
import boto3
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from models.jobs import Job
from db.models import Connector

class CloWMJob(BaseModel):
    parameters: dict|None = None
    logs_s3_path: str|None = None
    provenance_s3_path: str|None = None
    debug_s3_path: str|None = None
    workflow_version_id: str|None = None
    notes: str|None = None
    mode_id: str|None = None  

def connect_to_s3():
    load_dotenv(override=True)
    
    return boto3.client(
        's3',
        endpoint_url='https://s3.nfdi.bi.denbi.de',
        aws_access_key_id=os.getenv('CLOWM_S3_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('CLOWM_S3_SECRET_KEY')
    )

async def submit_data(jobDbId: str, s3Bucket: str):
    s3_client = connect_to_s3()    
    
    for file in os.listdir(f'{jobDbId}'):
        file_path=os.path.join(jobDbId, file)
        s3_client.upload_file(
            file_path,
            s3Bucket,
            f'{jobDbId}/{file}',
            ExtraArgs={
                "ContentType": "text/csv",
            }
        )

async def submit_job(job: Job, workflow_version_id: str):
    vcf = next((fileDataParameter.fileURL for fileDataParameter in job.fileDataParameters if fileDataParameter.parameterId == 'vcf'), None)

    load_dotenv(override=True)
    json = {
            "parameters": {
                "samples": f"s3://shape/{job.jobDbId}/germplasm.csv",
                "vcf": vcf,
                "observations": f"s3://shape/{job.jobDbId}/observations.csv",
                "outdir": f"s3://shape/{job.jobDbId}/output"
            },
            "logs_s3_path": f"s3://shape/{job.jobDbId}/logs",
            "provenance_s3_path": f"s3://shape/{job.jobDbId}/provenance",
            "debug_s3_path": f"s3://shape/{job.jobDbId}/debug",
            "workflow_version_id": workflow_version_id,
            "notes": "Started from BrOKER"
        }
    
    response = requests.post(
        url='https://clowm.bi.denbi.de/api/v1/workflow_executions', 
        json={
            "parameters": {
                "samples": f"s3://shape/{job.jobDbId}/germplasm.tsv",
                "vcf": vcf,
                "phenotypes": f"s3://shape/{job.jobDbId}/observations.tsv",
                "outdir": f"s3://shape/{job.jobDbId}/output"
            },
            "logs_s3_path": f"s3://shape/{job.jobDbId}/logs",
            "provenance_s3_path": f"s3://shape/{job.jobDbId}/provenance",
            "debug_s3_path": f"s3://shape/{job.jobDbId}/debug",
            "workflow_version_id": workflow_version_id,
            "notes": "Started from BrOKER"
        }, 
        headers={
            'X-CLOWM-TOKEN': os.getenv('CLOWM_API_TOKEN')
        }
    )
    response.raise_for_status()
    return response.json()

async def get_job_status(job: Job):
    load_dotenv(override=True)

    response = requests.get(
        url=f'https://clowm.bi.denbi.de/api/v1/workflow_executions/{job.additionalInfo["execution_id"]}', 
        headers={
            'X-CLOWM-TOKEN': os.getenv('CLOWM_API_TOKEN')
        }
    )

    response.raise_for_status()

    return response.json()

async def list_files(bucket: str, jobDbId: str):
    load_dotenv(override=True)
    
    s3_client = connect_to_s3()
    
    response = s3_client.list_objects(
        Bucket=bucket,
        Prefix=jobDbId
    )
    
    files = []
    
    for file in response['Contents']:
        if file['Size']>0:
            files.append(file['Key'])    

    return files

async def retrieve_file(bucket: str, fileURL: str):
    load_dotenv(override=True)
    
    s3_client = connect_to_s3()
    
    response = s3_client.get_object(
        Bucket=bucket,        
        Key=fileURL
    )
    
    return response


async def retrieve_files_as_zip(bucket: str, jobDbId: str):
    _, temp_zip_path = tempfile.mkstemp(suffix='.zip')
    
    load_dotenv(override=True)
    
    s3_client = connect_to_s3()
    
    response = s3_client.list_objects(
        Bucket=bucket,
        Prefix=jobDbId
    )
    
    files = []
    
    for file in response['Contents']:
        if file['Size']>0:
            files.append(file['Key'])
    
    with zipfile.ZipFile(temp_zip_path, 'w') as zipf:
        for file in files:
            response = s3_client.get_object(
                Bucket=bucket,        
                Key=file
            )
            filename = '/'.join(file.split('/')[-2:])
            zipf.writestr(filename, response['Body'].read())
    
    return temp_zip_path