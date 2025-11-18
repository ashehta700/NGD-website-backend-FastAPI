#response.py
def success_response(message: str, data: dict = None):
    return {
        "success": True,
        "message": message,
        "data": data
    }

def error_response(message: str, error_code: str):
    return {
        "success": False,
        "message": message,
        "error_code": error_code
    }
