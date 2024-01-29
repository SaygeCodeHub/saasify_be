"""Contains DTO classes"""


class ResponseDTO:
    """Response DTO"""

    def __init__(self, status, message, data):
        self.status = status
        self.message = message
        self.data = data


class ExceptionDTO:
    """Exception DTO"""
    def __init__(self,method,exception):
        self.method = method
        self.exception = exception
