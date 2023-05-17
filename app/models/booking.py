class Booking:
    def __init__(
        self,
        event_id: str,
        reserver_id: str,
        id: str,
        verified: bool,
        verified_time: str,
    ):
        self.event_id = event_id
        self.reserver_id = reserver_id
        self.id = id
        self.verified = verified
        self.verified_time = verified_time
