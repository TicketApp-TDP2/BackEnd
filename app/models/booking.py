class Booking:
    def __init__(self, event_id: str, reserver_id: str, id: str, verified: bool):
        self.event_id = event_id
        self.reserver_id = reserver_id
        self.id = id
        self.verified = verified
