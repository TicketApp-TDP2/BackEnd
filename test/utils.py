import copy
import datetime


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


def mock_date(monkeypatch, date):
    class MyDatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return cls(date["year"], date["month"], date["day"], date["hour"])

    monkeypatch.setattr(datetime, 'datetime', MyDatetime)
