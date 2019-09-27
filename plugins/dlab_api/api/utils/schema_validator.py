from jsonschema import validate, ValidationError


def validate_schema(request_data, schema):
    try:
        validate(request_data, schema)
        return 1
    except Exception:
        return 0
