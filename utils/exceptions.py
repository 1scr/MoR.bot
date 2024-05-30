"""
Ces exceptions serviront simplement pour du debug
"""

# Families

class NoFamilyError(Exception):
    def __init__(self, message):
        super().__init__(message)

class AlreadyInFamilyError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)

class UnavailableNameError(Exception):
    def __init__(self, message):
        super().__init__(message)

class UnavailableColorError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


# Inventory

class NoMissileError(Exception):
    def __init__(self, message):
        super().__init__(message)

class NoPlaneError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)