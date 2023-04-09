from typing import List


class Organizer:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        id: str,
        profession: str,
        about_me: str,
        profile_picture: str,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.id = id
        self.profession = profession
        self.about_me = about_me
        self.profile_picture = profile_picture

