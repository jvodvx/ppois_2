class SalonError(Exception):
    """Базовое исключение системы."""
    pass


class NotFoundError(SalonError):
    """Сущность не найдена."""
    pass


class BookingError(SalonError):
    """Ошибка записи."""
    pass


class ValidationError(SalonError):
    """Ошибка валидации данных."""
    pass


class ScheduleError(SalonError):
    """Ошибка расписания мастера."""
    pass