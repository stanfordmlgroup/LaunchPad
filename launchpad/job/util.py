#https://github.com/microsoft/nni/blob/master/nni/experiment/config/util.py
import math


_time_units = {'d': 24 * 3600, 'h': 3600, 'm': 60, 's': 1}
_size_units = {'gb': 1024 * 1024 * 1024, 'mb': 1024 * 1024, 'kb': 1024}

def parse_time(time: str, target_unit: str = 's') -> int:
    return _parse_unit(time.lower(), target_unit, _time_units)

def parse_size(size: str, target_unit: str = 'mb') -> int:
    return _parse_unit(size.lower(), target_unit, _size_units)

def _parse_unit(string, target_unit, all_units):
    for unit, factor in all_units.items():
        if string.endswith(unit):
            number = string[:-len(unit)]
            value = float(number) * factor
            return math.ceil(value / all_units[target_unit])
    raise ValueError(f'Unsupported unit in "{string}"')
