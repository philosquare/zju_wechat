from enum import Enum, unique


@unique
class Instrument(Enum):
    F20 = 'F20'
    New_F20 = 'New_F20'
    Old_F20 = 'Old_F20'
    FIB = 'FIB'

if __name__ == '__main__':
    print(Instrument.FIB)
