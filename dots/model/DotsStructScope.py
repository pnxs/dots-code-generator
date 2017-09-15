from enum import Enum

class DotsStructScope(Enum):
    PROGRAM = 0
    SERVER = 1
    SITE = 2
    GLOBAL = 3

    __dots_enum__ = {
        1: PROGRAM,
        2: SERVER,
        3: SITE,
        4: GLOBAL,
    }

    __enum_dots__ = {
    PROGRAM: 1,
    SERVER: 2,
    SITE: 3,
    GLOBAL: 4,
}