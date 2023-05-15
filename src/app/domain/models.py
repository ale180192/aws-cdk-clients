from pydantic import BaseModel, Field, validator

class Client(BaseModel):
    name: str = Field(..., description="Nombre del cliente")
    last_name: str = Field(..., description="Apellido del cliente")
    phone: str = Field(..., description="Número de teléfono de 10 dígitos")
    age: int = Field(..., description="edad del cliente")

    @validator('name')
    def validate_name(cls, value):
        if not value:
            raise ValueError("El nombre del cliente es requerido")
        return value

    @validator('last_name')
    def validate_last_name(cls, value):
        if not value:
            raise ValueError("El apellido del cliente es requerido")
        return value

    @validator('phone')
    def validate_phone(cls, value):
        if len(value) != 10:
            raise ValueError("El número de teléfono debe tener 10 dígitos")
        return value

    @validator('age')
    def validate_age(cls, value):
        if value < 18:
            raise ValueError("La edad debe ser mayor o igual a 18 años")
        return value