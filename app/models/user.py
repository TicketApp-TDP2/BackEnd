from typing import List, Optional


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
        favourites: List[str],
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.id = id
        self.birth_date = birth_date
        self.identification_number = identification_number
        self.phone_number = phone_number
        self.favourites = favourites

    def add_favourite(self, favourite: str):
        if favourite not in self.favourites:
            self.favourites.append(favourite)

    def remove_favourite(self, favourite: str):
        if favourite in self.favourites:
            self.favourites.remove(favourite)
