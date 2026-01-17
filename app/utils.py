import re


def parse_uins(uins: str) -> list[str]:
    uins_arr = uins.split()
    uins_arr = [re.sub(r'\D', '', item) for item in uins_arr if item]
    uins_arr = [item for item in uins_arr if item]

    return uins_arr
