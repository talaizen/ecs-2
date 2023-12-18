from pydantic import BaseModel, field_validator, model_validator


class TokenResponse(BaseModel):
    """
    Pydantic model representing a token response.

    Attributes:
        redirect_url (str): URL to redirect the user to after token generation.
    """

    redirect_url: str


class User(BaseModel):
    """
    Pydantic model for a user.

    Attributes:
        type (str): Type of the user (e.g., 'master', 'client').
        full_name (str): Full name of the user.
        personal_id (int): Personal identification number.
        password (str): User's password.
        email (str): Email address of the user.
        palga (str, optional): Additional attribute for the user, defaults to None.
        team (str, optional): Team to which the user belongs, defaults to None.
    """

    type: str
    full_name: str
    personal_id: int
    password: str
    email: str
    palga: str or None = None
    team: str or None = None


class LoginForm(BaseModel):
    """
    Pydantic model for login form data.

    Attributes:
        personal_id (int): Personal identification number.
        password (str): Password for login.
    """

    personal_id: int
    password: str

    @field_validator("personal_id", "password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        """
        Field validator to ensure the field is not empty.

        Args:
            v (str): Value to be validated.

        Raises:
            ValueError: If the field is empty.

        Returns:
            str: Validated value.
        """
        if v == "":
            raise ValueError("all fields are required")
        return v


class MasterAccount(BaseModel):
    """
    Pydantic model for a master account.

    Attributes:
        first_name (str): First name of the master account holder.
        last_name (str): Last name of the master account holder.
        personal_id (int): Personal identification number.
        email (str): Email address.
        password (str): Password for the account.
        confirm_password (str): Confirmation of the password.
        master_password (str): Master password for additional security.
    """

    first_name: str
    last_name: str
    personal_id: int
    email: str
    password: str
    confirm_password: str
    master_password: str

    @field_validator(
        "first_name",
        "last_name",
        "email",
        "password",
        "confirm_password",
        "master_password",
    )
    @classmethod
    def not_empty(cls, v: str) -> str:
        if v == "":
            raise ValueError("all fields are required")
        return v

    @model_validator(mode="after")
    def check_passwords_match(self) -> "MasterAccount":
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("passwords do not match")
        return self

    @field_validator("personal_id")
    @classmethod
    def validate_personal_id(cls, v):
        if len(str(v)) < 7:
            raise ValueError("personal id must include at least 7 digits")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def capitalize(cls, v: str) -> str:
        return v.capitalize()


class ClientAccount(BaseModel):
    """
    Pydantic model for a client account.

    Attributes:
        palga (str): Attribute specific to client accounts.
        team (str): Team name or identifier.
        first_name (str): First name of the client account holder.
        last_name (str): Last name of the client account holder.
        personal_id (int): Personal identification number.
        email (str): Email address.
        password (str): Password for the account.
        confirm_password (str): Confirmation of the password.
        master_password (str): Master password for additional security.
    """

    palga: str
    team: str
    first_name: str
    last_name: str
    personal_id: int
    email: str
    password: str
    confirm_password: str
    master_password: str

    @field_validator(
        "first_name",
        "last_name",
        "palga",
        "team",
        "email",
        "password",
        "confirm_password",
        "master_password",
    )
    @classmethod
    def not_empty(cls, v: str) -> str:
        if v == "":
            raise ValueError("all fields are required")
        return v

    @model_validator(mode="after")
    def check_passwords_match(self) -> "ClientAccount":
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("passwords do not match")
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