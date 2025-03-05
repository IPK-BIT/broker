from litestar import Router
from routes.files.controllers.files import FileController

FilesRouter = Router(
    path="/api/v1",
    tags=["Files"],
    route_handlers=[FileController]
)