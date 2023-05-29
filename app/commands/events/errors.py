from app.models.errors import BusinessError


class EventNotFoundError(BusinessError):
    def __init__(self):
        msg = "event_not_found"
        super().__init__(msg)


class EventAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "event_already_exists"
        super().__init__(msg)


class AgendaEmptyError(BusinessError):
    def __init__(self):
        msg = "agenda_can_not_be_empty"
        super().__init__(msg)


class AgendaEmptySpaceError(BusinessError):
    def __init__(self):
        msg = "agenda_can_not_have_empty_spaces"
        super().__init__(msg)


class AgendaOverlapError(BusinessError):
    def __init__(self):
        msg = "agenda_can_not_have_overlap"
        super().__init__(msg)


class AgendaTooLargeError(BusinessError):
    def __init__(self):
        msg = "agenda_can_not_end_after_event_end"
        super().__init__(msg)


class EventNotBorradorError(BusinessError):
    def __init__(self):
        msg = "event_is_not_in_borrador_statee"
        super().__init__(msg)


class TooManyImagesError(BusinessError):
    def __init__(self):
        msg = "max_number_of_images_is_10"
        super().__init__(msg)


class TooManyFaqsError(BusinessError):
    def __init__(self):
        msg = "max_number_of_faqs_is_30"
        super().__init__(msg)


class EventCannotBeUpdatedError(BusinessError):
    def __init__(self):
        msg = "event_cannot_be_updated"
        super().__init__(msg)


class VacantsCannotBeUpdatedError(BusinessError):
    def __init__(self):
        msg = "vacants_cannot_be_less_than_bookings"
        super().__init__(msg)


class EventCannotBeSuspendedError(BusinessError):
    def __init__(self):
        msg = "event_cannot_be_suspended"
        super().__init__(msg)


class EventCannotBeUnSuspendedError(BusinessError):
    def __init__(self):
        msg = "event_cannot_be_unsuspended"
        super().__init__(msg)


class CollaboratorNotFoundError(BusinessError):
    def __init__(self):
        msg = "collaborator_not_found"
        super().__init__(msg)


class EventTimeError(BusinessError):
    def __init__(self):
        msg = "end_time_must_be_greater_than_start_time"
        super().__init__(msg)


class AgendaDoesNotEndError(BusinessError):
    def __init__(self):
        msg = "agenda_can_not_end_before_event_ends"
        super().__init__(msg)
