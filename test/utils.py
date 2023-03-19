import copy


def generate_invalid(correct, invalid):
    result = []
    for key in correct.keys():
        if key not in invalid:
            continue
        for invalid_value in invalid[key]:
            cp = copy.deepcopy(correct)
            if invalid_value is None:
                del cp[key]
            else:
                cp[key] = invalid_value
            result.append(cp)
    return result
