from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length, Email
import re


def validate_phone(value):
    # simple phone validation: digits, spaces, +, -, ()
    if value is None:
        return
    if not re.match(r'^[0-9\s\+\-\(\)]+$', value):
        raise ValidationError('Invalid phone number format')


class CustomerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=1, max=200))
    email = fields.Email(required=False, validate=Email())
    phone = fields.Str(required=False, validate=validate_phone)
    address = fields.Str(required=False)
    is_active = fields.Bool()
    owner_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
