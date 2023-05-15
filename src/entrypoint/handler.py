from fastapi import (
    FastAPI,
    HTTPException,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import (
    JSONResponse,
)
from mangum import Mangum

from app.api.endpoints.clients_endpoints import ClientsRouter
from app.utils import logger as _logger
from app.adapters.http.models import responses

logger = _logger.get_logger()




app = FastAPI(
    title="Dish clients API service.",
    openapi_url="/prod/openapi.json"
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)




@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []
    for error in exc.errors():
        field = error['loc'][1]
        message = error['msg']
        errors.append({field: message})

    error_detail = responses.ErrorDetailResponse(
        error_code="BAD_REQUEST",
        error_detail="Bad request.",
        errors=errors
    )
    return JSONResponse(
        status_code=422,
        content=responses.ErrorResponse(error=error_detail.dict()).dict()
    )


# Routers
clients_router = ClientsRouter()

app.include_router(clients_router.router)

main = Mangum(app)