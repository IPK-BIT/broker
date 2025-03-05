import base64
import os
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from litestar import Controller, get, post, Response as LitestarResponse, status_codes
from models.responses import Response, Metadata, Result, Pagination, Message, SingleResponse
from models.files import File, FileSearch, FileContent, ArchiveRequest
from connectors import clowm


class FileController(Controller):
    path='/files'
    
    @get('/')
    async def get_all_files_metadata(self, transaction: AsyncSession, jobDbId: str) -> Response[File]:
        
        files = await clowm.list_files('shape', jobDbId+'/output')
        
        data=[]
        for file in files:
            data.append(File(
                fileURL=file,
                fileName=file.split('/')[-1]
            ))
        
        return Response(
            metadata=Metadata(
                pagination=Pagination(
                    currentPage=0,
                    pageSize=1000,
                    totalPages=1,
                    totalCount=1
                ),
                datafiles=[],
                status=[
                    Message(
                        message='Successfully retrieved metadata for all files',
                        type='INFO'
                    )
                ]
            ),
            result=Result(
                data=data,
            )
        )
        
    @post('/archive')
    async def get_as_archive(self, transaction: AsyncSession, data: ArchiveRequest) -> None:
        temp_zip_path = await clowm.retrieve_files_as_zip(data.bucket, data.jobDbId+'/output')
        
        ic(temp_zip_path)
        
        with open(temp_zip_path, 'rb') as f:
            zip_content = f.read()
        
        os.remove(temp_zip_path)
        
        headers = {"Content-Disposition": "attachment; filename=files.zip"}
        return LitestarResponse(zip_content, media_type="application/zip", status_code=status_codes.HTTP_200_OK, headers=headers)
    
    @post('/retrieve/content')
    async def retrieve_file_content(self, transaction: AsyncSession, data: FileSearch) -> None:#SingleResponse[FileContent]:
        file = await clowm.retrieve_file(data.bucket, data.fileURL)
        
        fileContent = file['Body'].read()
        
        if data.encoding=='raw':
            data = fileContent
            return data
        else:
            data = base64.b64encode(fileContent).decode('utf-8')
        
        return SingleResponse(
            metadata=Metadata(
                status=[
                    Message(
                        message='Successfully retrieved file content',
                        type='INFO'
                    )
                ],
                pagination=Pagination(
                    currentPage=0,
                    pageSize=1,
                    totalPages=1,
                    totalCount=1
                ),
                datafiles=[],
            ),
            result=FileContent(
                data=data,
                mimeType=file['ContentType'],
                contentSize=file['ContentLength']
            )
        )