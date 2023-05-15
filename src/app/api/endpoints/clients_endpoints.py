from typing import Any
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException
)
from app.domain.service_layer import clients_service
from app.utils.logger import get_logger
from app.domain.models import (
    Client
)
from app.adapters.http.models.responses import (
    ErrorResponse,
    ClientsFullResponse,
    SuccessCreatedResponse,
    ClientFullResponse
)
from app.adapters.http.models import requests
from app.adapters.http import http_utils
# from app.config import Settings, get_settings

_logger = get_logger()
router = APIRouter()

class ClientsRouter:
    
    def __init__(self) -> None:
        pass

    @property
    def router(self):
        api_router = APIRouter(prefix="/v1/clients", tags=["Clients"])


        @api_router.post(
            "/",
            response_model=SuccessCreatedResponse,
            responses={400: {"model": ErrorResponse}},
            status_code=201,
        )
        def create(
            client_request: requests.ClientRequest,
            clients_service: clients_service.ClientsService = Depends(clients_service.ClientsService),
        ):
            try:
                _logger.info(client_request)
                resp = clients_service.create_client(
                    phone=client_request.phone,
                    name=client_request.client_name.name,
                    last_name=client_request.client_name.last_name,
                    age=client_request.age,
                )
                response_model = http_utils.get_success_response(data={"mensaje": "Cliente creado exitosamente"})
                return response_model
            
            except clients_service.ObjectAlreadyExists as e:
                error = ErrorResponse(error={"error_code": "ObjectAlreadyExists"})
                raise HTTPException(status_code=400, detail=error.dict())
            
    
        @api_router.get(
            "/list",
            response_model=ClientsFullResponse,
            status_code=200,
        )
        def list(
            clients_service: clients_service.ClientsService = Depends(clients_service.ClientsService),
        ):
            _logger.info("list clients.")
            resp = clients_service.list_clients()
            _logger.info(resp)
            response_model = http_utils.get_success_response(data=resp)
            return response_model
        

        @api_router.get(
            "/{client_phone}",
            response_model=ClientFullResponse,
            responses={404: {"model": ErrorResponse}},
            status_code=200,
        )
        def detail(
            client_phone: str,
            clients_service: clients_service.ClientsService = Depends(clients_service.ClientsService),
        ):
            try:
                _logger.info("Client detail.")
                client = clients_service.get_client(client_phone)
                _logger.info(client)
                response_model = http_utils.get_success_response(data=client)
                return response_model
            except clients_service.ObjectDoesNotExist as e:
                error = ErrorResponse(error={"error_code": "ObjectDoesNotExist"})
                raise HTTPException(status_code=404, detail=error.dict())

            
        return api_router