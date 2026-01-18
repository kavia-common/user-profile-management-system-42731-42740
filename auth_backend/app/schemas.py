from marshmallow import Schema, fields, validate


class ErrorSchema(Schema):
    code = fields.Int(required=True, description="HTTP status code")
    error = fields.Str(required=True, description="Short error name")
    message = fields.Str(required=True, description="Human-readable message")
    details = fields.Dict(required=False, description="Optional field-level details")


class RegisterRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    display_name = fields.Str(required=False, validate=validate.Length(max=120))
    bio = fields.Str(required=False, validate=validate.Length(max=1000))


class LoginRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class AuthResponseSchema(Schema):
    access_token = fields.Str(required=True)
    token_type = fields.Str(required=True)
    expires_in_minutes = fields.Int(required=True)


class ProfileSchema(Schema):
    id = fields.Int(required=True)
    email = fields.Email(required=True)
    display_name = fields.Str(allow_none=True)
    bio = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)


class ProfileUpdateRequestSchema(Schema):
    display_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=120))
    bio = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))


class MessageSchema(Schema):
    message = fields.Str(required=True)
