from datetime import datetime


def to_naive_utc(value: datetime) -> datetime:
    """Normaliza a datetime naive (UTC).

    Mongo/Beanie siempre devuelve datetimes naive; un valor que llega del
    request puede venir tz-aware. Comparar los dos sin normalizar primero
    lanza `TypeError: can't compare offset-naive and offset-aware datetimes`.
    """
    return value.replace(tzinfo=None) if value.tzinfo else value
