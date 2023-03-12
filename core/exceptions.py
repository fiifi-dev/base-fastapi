from fastapi import HTTPException, status


class NotFound(HTTPException):
    def __init__(self, detail="Resource requested was not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class NotAuthenticated(HTTPException):
    def __init__(self, detail="You are not authenticated"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class PermissionDenied(HTTPException):
    def __init__(self, detail="You don't have permission to access this resource"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequest(HTTPException):
    def __init__(self, detail="You don't have permission to access this resource"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)