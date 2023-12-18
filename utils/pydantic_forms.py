from pydantic import BaseModel, field_validator, model_validator


class TokenResponse(BaseModel):
    redirect_url: str


class User(BaseModel):
    type: str
    full_name: str 
    personal_id: int
    password: str
    email: str
    palga: str or None = None
    team: str or None = None


class LoginForm(BaseModel):
    personal_id: int
    password: str

    @field_validator("personal_id", "password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if v == '':
            raise ValueError('all fields are required')
        return v


class MasterAccount(BaseModel):
    first_name: str
    last_name: str
    personal_id: int
    email: str
    password: str
    confirm_password: str
    master_password: str


    @field_validator("first_name", "last_name", "email", "password", "confirm_password", "master_password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if v == '':
            raise ValueError('all fields are required')
        return v

    @model_validator(mode="after")
    def check_passwords_match(self) -> "MasterAccount":
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')
        return self
    
    @field_validator("personal_id")
    @classmethod
    def validate_personal_id(cls, v):
        if len(str(v)) < 7:
            raise ValueError("personal id must include at least 7 digits")
        return v
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def capitalize(cls, v: str) -> str:
        return v.capitalize()


class ClientAccount(BaseModel):
    palga: str
    team: str
    first_name: str
    last_name: str
    personal_id: int
    email: str
    password: str
    confirm_password: str
    master_password: str


    @field_validator("first_name", "last_name", "palga", "team", "email", "password", "confirm_password", "master_password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if v == '':
            raise ValueError('all fields are required')
        return v
    
    @model_validator(mode="after")
    def check_passwords_match(self) -> "ClientAccount":
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')
        return self
    
    @field_validator("personal_id")
    @classmethod
    def validate_personal_id(cls, v) -> int:
        if len(str(v)) < 7:
            raise ValueError("personal id must include at least 7 digits")
        return v
    
    @field_validator("first_name", "last_name", "palga", "team")
    @classmethod
    def capitalize(cls, v: str) -> str:
        return v.capitalize()

