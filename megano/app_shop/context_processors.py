import re
from typing import Any

from django.db.models import Sum

from app_shop.models import Category, Tag, Product


regex = r"(\/admin[\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"


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
    current_price_of_products = [item.current_price for item in Product.objects.order_by('price')]
    min_price_in_catalog = str(min(current_price_of_products))
    max_price_in_catalog = str(max(current_price_of_products))
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
    popular_product_pk = (Product.objects.filter(quantity__gt=0).annotate(
        Sum('ordered_products__quantity')
    ).order_by(
        '-ordered_products__quantity__sum'
    ).first().pk)
    context = {
        'popular_product_pk': popular_product_pk
    }
    return context
