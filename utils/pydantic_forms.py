from typing import List
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
        if v == "":
            raise ValueError("all fields are required")
        return v


class MasterAccount(BaseModel):
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

class UpdateInventoryCollectionItem(BaseModel):
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
    
class UpdateClientUserCollectionItem(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    personal_id: int
    email: str
    palga: str
    team: str
    password: str

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

class ClientUserObjectId(BaseModel):
    user_id: str

class SwitchRequestObjectId(BaseModel):
    switch_request_id: str

class CanceledSwitchRequest(BaseModel):
    canceled_request_id: str

class AddSigningData(BaseModel):
    selected_items: List[PendingSigningObjectId]

class ApproveSwitchRequestData(BaseModel):
    selected_requests: List[SwitchRequestObjectId]

class RejectSwitchRequestData(BaseModel):
    selected_requests: List[SwitchRequestObjectId]

class SwitchSigningData(BaseModel):
    selected_items: List[SwitchSelectedItem]
    signing_descrition: str

class InventoryCollectionItemUpdates(BaseModel):
    item_id: str
    name: str
    category: str
    total_count: int
    color: str
    palga: str
    mami_serial: str
    manufacture_mkt: str
    katzi_mkt: str
    serial_no: str
    description: str

class InventoryDelteItem(BaseModel):
    item_id: str

class InventoryAddItem(BaseModel):
    name: str
    category: str
    total_count: int
    color: str
    palga: str
    mami_serial: str
    manufacture_mkt: str
    katzi_mkt: str
    serial_no: str
    description: str

class NewKitLock(BaseModel):
    kit_name: str
    palga: str

class KitSelectedItem(BaseModel):
    item_id: str
    quantity: str

class NewKitItems(BaseModel):
    selected_items: List[KitSelectedItem]
    kit_descrition: str

class KitsCollectionItem(BaseModel):
    kit_id: str
    kit_name: str
    kit_description: str

class KitContent(BaseModel):
    kit_id: str

class KitContentCollectionItem(BaseModel):
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

class KitRemoveItemsCollectionItem(KitContentCollectionItem):
    kit_item_id: str

class RemoveKitItemSelectedItem(BaseModel):
    kit_item_id: str
    quantity: str

class RemoveKitItemData(BaseModel):
    selected_items: List[RemoveKitItemSelectedItem]

class ExistingKitAddItems(BaseModel):
    kit_id: str
    selected_items: List[KitSelectedItem]

class AddAmplifierTracking(BaseModel):
    item_id: str
    days_interval: int
    test_type: str

class AmplifierStatusItem(BaseModel):
    object_id: str
    name: str
    category: str
    color: str
    palga: str
    mami_serial: str
    description: str
    test_type: str
    interval: int
    results: str
    last_updated: str

class UpdateAmplifierResults(BaseModel):
    object_id: str
    results: str

class UpdateAmplifierInterval(BaseModel):
    object_id: str
    interval: int

class DeleteAmplifierTracking(BaseModel):
    object_id: str

class AmplifierTODOItem(BaseModel):
    name: str
    category: str
    color: str
    palga: str
    mami_serial: str
    description: str
    test_type: str
    interval: int
    results: str
    last_updated: str
    days_passed: int