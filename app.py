from litestar import Litestar
from routes.analysis.router import AnalysisRouter
from routes.files.router import FilesRouter
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.openapi.spec.server import Server

from db.connect import provide_transaction, db_connection

cors_config = CORSConfig(
    allow_origins=['*'],
    allow_methods=['GET', 'POST', 'OPTIONS']
)

app = Litestar(
    cors_config=cors_config,
    dependencies={'transaction': provide_transaction},
    lifespan=[db_connection],
    route_handlers=[AnalysisRouter, FilesRouter],
    openapi_config=OpenAPIConfig(
        title='BrOKER',
        version='0.1',
        render_plugins=[ScalarRenderPlugin()],
        path='/schema',
        servers=[Server('https://divportal.ipk-gatersleben.de')]
    )
)