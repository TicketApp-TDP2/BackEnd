from typing import List


class User:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        id: str,
        birth_date: str,
        identification_number: str,
        phone_number: str,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.id = id
        self.birth_date = birth_date
        self.identification_number = identification_number
        self.phone_number = phone_number
