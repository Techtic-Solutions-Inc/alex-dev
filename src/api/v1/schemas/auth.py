from pydantic import BaseModel, Field, model_validator


class LoginRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @model_validator(mode='after')
    def passwords_match(self) -> 'ResetPasswordRequest':
        if self.new_password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self


class ResetPasswordResponse(BaseModel):
    message: str = 'Your password has been reset successfully! You can now log in.'


class RequestPasswordResetRequest(BaseModel):
    email: str = Field(min_length=1)


class RequestPasswordResetResponse(BaseModel):
    message: str = (
        'If an account with that email exists, a password reset link has been sent.'
    )
