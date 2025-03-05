from litestar import Router
from routes.analysis.controllers.jobs import JobController
from routes.analysis.controllers.procedures import ProcedureController

AnalysisRouter = Router(
    path="/brapi/v2",
    tags=["Analysis"],
    route_handlers=[JobController, ProcedureController]
)