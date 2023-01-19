from typing import Any

from app_setting.models import Settings


# Получение валюты из базы данных.
def get_currency(request: Any) -> dict:
    """
    Метод получает валюту из базы данных и возвращает ее в виде словаря.

    :param request: Это объект запроса, который отправляется в представление.
    :type request: Any
    :return: Словарь с ключом «ВАЛЮТА» и значением валюты сайта.
    """
    CURRENCY = Settings.objects.first().CURRENT_SITE_CURRENCY
    context = {
        'CURRENCY': CURRENCY
    }
    return context
