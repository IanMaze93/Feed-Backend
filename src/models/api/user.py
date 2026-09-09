from pydantic import BaseModel


class SignupPayload(BaseModel):
    username: str
    password: str
    firstName: str
    lastName: str
    email: str


class LoginPayload(BaseModel):
    username: str
    password: str
