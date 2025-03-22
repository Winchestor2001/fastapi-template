class DatabaseError(Exception):
    pass


class IntegrityViolationError(Exception):
    pass


class FilteringError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserAlreadyVerified(Exception):
    pass