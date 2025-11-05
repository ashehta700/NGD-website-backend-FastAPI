def success_response(message: str, data=None):
    return {"success": True, "message": message, "data": data}

def error_response(message: str, code: str = "ERROR"):
    return {"success": False, "message": message, "error_code": code}

