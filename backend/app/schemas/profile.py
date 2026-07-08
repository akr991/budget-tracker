from pydantic import BaseModel, EmailStr


class ProfileResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True
