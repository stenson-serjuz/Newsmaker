class ParserError(Exception):
    pass


class RetryableParserError(ParserError):
    pass


class FatalParserError(ParserError):
    pass
