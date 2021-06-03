from enum import Enum


class Status(Enum):
    ACTIVE = 2
    FINISHED = 1
    FAILED = 0

    def __str__(self):
        return str(self.name).lower()


class Priority(Enum):
    HIGH = 2
    NORMAL = 1
    LOW = 0

    def __str__(self):
        return str(self.name).lower()
