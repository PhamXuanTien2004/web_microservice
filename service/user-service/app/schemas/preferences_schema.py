from marshmallow import Schema, fields, validate, ValidationError

class PreferencesSchema(Schema):
    """ Validate khi update preferences """
    email_alerts = fields.Boolean(required = False)
    sms_alerts = fields.Boolean(required = False)