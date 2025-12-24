class IAMError(Exception):
    pass


class IAMUnauthorized(IAMError):
    pass


class IAMUnavailable(IAMError):
    pass
