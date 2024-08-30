from functools import wraps
from fastapi import HTTPException

def api_handler(method: str, endpoint: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                print(f"{method} call made to /{endpoint}")
                response = await func(*args, **kwargs)
                print(f"{method} call to /{endpoint} successfully completed")
                return response
            except Exception as e:
                print(e)
                if isinstance(e, NameError):
                    raise HTTPException(status_code=409, detail=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        return wrapper
    return decorator




