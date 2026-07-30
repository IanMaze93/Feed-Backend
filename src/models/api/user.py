from pydantic import BaseModel


class CreateUserPayload(BaseModel):
    firstName: str
    lastName: str
    email: str
