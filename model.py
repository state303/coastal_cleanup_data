# data model / ERD representation
import datetime


# core
class CleanupAction:
    # individual ids
    id: int
    longitude: float
    latitude: float
    adult: int
    children: int
    weight: float
    distance: float
    cleaned_at: datetime.datetime
    # relational ids
    cleanup_type: int
    cleanup_group: int
    environment: int
    country: int
    zone: int
    state: int


################
# DEPENDENCIES #
################
class State:
    id: int | None
    name: str

    def __init__(self, id: int | None, name: str):
        self.id = id
        self.name = name.strip()


class Country:
    def is_valid(self) -> bool:
        return self.name is not None and len(self.name) > 0

    id: int
    name: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class CleanupGroup:
    id: int
    name: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class CleanupType:
    id: int
    name: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class Environment:
    id: int
    name: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class Zone:
    id: int
    name: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class Litter:
    id: int
    name: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class CleanupLitter:
    litter_id: int
    cleanup_id: int

    def __init__(self, litter_id: int, cleanup_id: int):
        self.litter_id = litter_id
        self.cleanup_id = cleanup_id
