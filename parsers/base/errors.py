class ParserError(Exception):
    pass


class RetryableParserError(ParserError):
    pass


class FatalParserError(ParserError):
    pass


class HTTPStatusError(RetryableParserError):
    def __init__(self, status_code: int) -> None:
        super().__init__(f"http_status:{status_code}")
        self.status_code = status_code
