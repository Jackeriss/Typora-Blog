from schema import Schema, Regex, SchemaError


def none_safe_str(data):
    if data is None:
        return ""
    else:
        return str(data)


def change_bool(param):
    if isinstance(param, bool):
        return param
    if isinstance(param, int) or param.isdigit():
        return bool(int(param))
    if isinstance(param, str):
        if param.lower() == "false":
            return False
        elif param.lower() == "true":
            return True
    return False


def list_parse(str_param, format_type=int):
    try:
        return [format_type(param) for param in str_param.strip().split(",")]
    except BaseException:
        return None


def validate_enum_type(enum_type):
    def _wrap(param):
        try:
            return enum_type(param)
        except Exception:
            raise SchemaError(f"not support type in {enum_type.__name__}")

    return _wrap


def email_schema():
    return Regex(
        r"^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$",
        error="Please enter a valid email.",
    )
