from bson.objectid import ObjectId
from typing import List
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
    

class InventoryCollectionItem(BaseModel):
    object_id: str
    name: str
    category: str
    count: str
    color: str
    palga: str
    mami_serial: str
    manufacture_mkt: str
    katzi_mkt: str
    serial_no: str
    description: str
    max_amount: int

class PendingSigningsCollectionItem(BaseModel):
    object_id: str
    name: str
    category: str
    quantity: int
    color: str
    palga: str
    mami_serial: str
    manufacture_mkt: str
    katzi_mkt: str
    serial_no: str
    item_description: str
    signer: str
    issuer: str
    signing_description: str

class SigningsCollectionItem(BaseModel):
    name: str
    category: str
    quantity: int
    color: str
    palga: str
    mami_serial: str
    manufacture_mkt: str
    katzi_mkt: str
    serial_no: str
    item_description: str
    signer: str
    issuer: str
    signing_description: str
    date: str

class SigningItem(BaseModel):
    signing_id: str
    name: str
    category: str
    quantity: int
    color: str
    palga: str
    mami_serial: str
    manufacture_mkt: str
    katzi_mkt: str
    serial_no: str
    item_description: str
    signer: str
    issuer: str
    signing_description: str
    date: str

class SwitchRequestItem(BaseModel):
    request_id: str
    name: str
    category: str
    quantity: int
    color: str
    palga: str
    mami_serial: str
    manufacture_mkt: str
    katzi_mkt: str
    serial_no: str
    item_description: str
    signer: str
    signing_description: str
    new_signer: str
    switch_description: str
    status: str
    
class ClientUserCollectionItem(BaseModel):
    first_name: str
    last_name: str
    personal_id: int
    email: str
    palga: str
    team: str

class LogCollectionItem(BaseModel):
    action: str
    description: str
    date: str

class NewSigningAccessForm(BaseModel):
    signer_personal_id: int
    master_password: str

class SwitchSigningAccessForm(BaseModel):
    old_personal_id: str
    new_personal_id: str
    master_password: str

class ClientSwitchSigningAccessForm(BaseModel):
    new_personal_id: str
    client_password: str


class ClientUser(BaseModel):
    first_name: str
    last_name: str
    personal_id: int
    email: str
    palga: str
    team: str

class MasterUser(BaseModel):
    first_name: str
    last_name: str
    personal_id: int
    email: str

class SigningSelectedItem(BaseModel):
    item_id: str
    quantity: str

class SwitchSelectedItem(BaseModel):
    signing_id: str
    quantity: str

class RemoveSigningSelectedItem(BaseModel):
    signing_id: str
    quantity: str

class NewSigningData(BaseModel):
    selected_items: List[SigningSelectedItem]
    signing_descrition: str

class RemoveSigningData(BaseModel):
    selected_items: List[RemoveSigningSelectedItem]

class PendingSigningObjectId(BaseModel):
    pending_signing_id: str

class AddSigningData(BaseModel):
    selected_items: List[PendingSigningObjectId]

class SwitchSigningData(BaseModel):
    selected_items: List[SwitchSelectedItem]
    signing_descrition: str



