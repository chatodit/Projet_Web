from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Uniform error response format for the entire API.

    All error responses follow:
    {
        "error": true,
        "status_code": 400,
        "message": "Human-readable summary",
        "details": { ... }  // field-level errors if applicable
    }
    """
    response = exception_handler(exc, context)

    if response is None:
        return response

    errors = response.data
    status_code = response.status_code

    # Build a human-readable message from DRF's error structure
    if isinstance(errors, list):
        message = " ".join(str(e) for e in errors)
        details = None
    elif isinstance(errors, dict):
        if "detail" in errors:
            message = str(errors["detail"])
            details = None
        else:
            messages = []
            for field, field_errors in errors.items():
                if isinstance(field_errors, list):
                    messages.append(f"{field}: {', '.join(str(e) for e in field_errors)}")
                else:
                    messages.append(f"{field}: {field_errors}")
            message = "; ".join(messages)
            details = errors
    else:
        message = str(errors)
        details = None

    response.data = {
        "error": True,
        "status_code": status_code,
        "message": message,
    }
    if details:
        response.data["details"] = details

    return response
