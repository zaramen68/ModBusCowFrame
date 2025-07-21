from dataclasses import dataclass

""" Структура сообщения от рамки, заполняется при каждом опросе рамки"""
@dataclass
class Message:
    """Время *20 ms прошедшее с последнего срабатывания метки fdx. макимальное значение 255"""
    fdx_time: int | None = None
    """id fdx метки"""
    fdx_id: int | None = None
    """rssi fdx метки"""
    fdx_rssi: int | None = None
    """Время *20 ms прошедшее с последнего срабатывания метки hdx. макимальное значение 255"""
    hdx_time: int | None = None
    """id hdx метки"""
    hdx_id: int | None = None
    """rssi hdx метки"""
    hdx_rssi: int | None = None
    """Состояние ответа. Если ошибка -  false"""
    is_valid: bool = False
    """Текст последней ошибки"""
    last_error: str | None = None
    """ Время создания сообщения """
    time_stamp: float = 0