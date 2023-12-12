from pydantic import BaseModel


class LoginForm(BaseModel):
    username: str
    password: str

class MasterAccount(BaseModel):
    first_name: str
    last_name: str
    personal_id: int
    email: str
    password: str