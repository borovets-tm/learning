import re
from typing import Any

from django.db.models import Min, Max, Sum

from app_shop.models import Category, Cart, Tag, Good, Settings

regex = r"(\/[admin][\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"


# Чтобы меню с категориями товаров работало на каждой странице.
def get_category_list_for_menu(request: Any) -> dict:
    """
    Если текущий URL связан с административной панелью возвращает пустой словарь.
    В противном случае вернуть словарь, содержащий список всех категорий.

    :param request: Любой.
    :type request: Any
    :return: Словарь с ключом category_list и значением всех категорий в базе данных.
    """
    if re.search(regex, request.META['PATH_INFO']):
        return {}
    category_list = Category.objects.all()
    context = {
        'category_list': category_list
    }
    return context


# Получаем инфу о корзине пользователя на каждой странице
def get_info_about_users_basket(request: Any) -> dict:
    """
    Если текущий URL связан с административной панелью возвращает пустой словарь.
    Возвращает словарь с суммой товаров в корзине и количеством товаров в корзине пользователя.

    :param request: Любой - объект запроса.
    :type request: Any
    :return: Словарь с суммой товаров в корзине и количеством товаров в корзине пользователя.
    """
    if re.search(regex, request.META['PATH_INFO']):
        return {}
    if request.user.id:
        user_cart = request.user.user_cart
        amount = user_cart.amount if user_cart.amount else 0
        number_of_goods = user_cart.number_of_goods if user_cart.number_of_goods else 0
    else:
        user_cart = Cart.objects.get(session=request.META.get('CSRF_COOKIE'))
        amount = user_cart.amount if user_cart.amount else 0
        number_of_goods = user_cart.number_of_goods if user_cart.number_of_goods else 0
    context = {
        'amount': amount,
        'number_of_goods': number_of_goods
    }
    return context


# Получение списка популярных тегов для фильтра.
def get_popular_tags(request: Any) -> dict:
    """
    Возвращает словарь популярных тегов, если текущий URL не является административной панелью.

    :param request: Any - объект запроса.
    :type request: Any
    :return: Словарь с ключом popular_tags_list и значением списка тегов.
    """
    if re.search(regex, request.META['PATH_INFO']):
        return {}
    popular_tags_list = Tag.objects.order_by('-number_of_requests')[:6]
    context = {
        'popular_tags_list': popular_tags_list
    }
    return context


# Получение минимальной и максимальной цены товара в каталоге.
def get_min_and_max_price(request: Any) -> dict:
    """
    Если текущий URL связан с административной панелью возвращает пустой словарь.
    Возвращает словарь с минимальной и максимальной ценой товаров в каталоге.

    :param request: Любой - объект запроса.
    :type request: Any
    :return: Словарь с минимальной и максимальной ценой товара в каталоге.
    """
    if re.search(regex, request.META['PATH_INFO']):
        return {}
    min_price_in_catalog = str(Good.objects.aggregate(Min('current_price'))['current_price__min']).replace(' ', '')
    max_price_in_catalog = str(Good.objects.aggregate(Max('current_price'))['current_price__max']).replace(' ', '')
    context = {
        'min_price_in_catalog': min_price_in_catalog,
        'max_price_in_catalog': max_price_in_catalog
    }
    return context


# Получение самого популярного товара в каталоге.
def get_the_most_popular_item(request: Any) -> dict:
    """
    Если текущий URL связан с административной панелью возвращает пустой словарь.
    Возвращает первичный ключ самого популярного товара.

    :param request: Any - объект запроса.
    :type request: Any
    :return: Упак. самого популярного товара.
    """
    if re.search(regex, request.META['PATH_INFO']):
        return {}
    popular_good_pk = (Good.objects.filter(quantity__gt=0)
                       .annotate(Sum('ordered_goods__quantity'))
                       .order_by('-ordered_goods__quantity__sum').first().pk
                       )
    context = {
        'popular_good_pk': popular_good_pk
    }
    return context

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
