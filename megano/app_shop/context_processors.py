from typing import Any

from django.db.models import Min, Max

from app_shop.models import Category, Cart, Tag, Good


# Чтобы меню с категориями товаров работало на каждой странице.
def get_category_list_for_menu(request: Any) -> dict:
    category_list = Category.objects.all()
    context = {
        'category_list': category_list
    }
    return context


# Получаем инфу о корзине пользователя на каждой странице
def get_info_about_users_basket(request: Any) -> dict:
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


def get_popular_tags(request: Any) -> dict:
    popular_tags_list = Tag.objects.order_by('-number_of_requests')[:6]
    context = {
        'popular_tags_list': popular_tags_list
    }
    return context


def get_min_and_max_price(request: Any) -> dict:
    min_price_in_catalog = str(Good.objects.aggregate(Min('current_price'))['current_price__min']).replace(' ', '')
    max_price_in_catalog = str(Good.objects.aggregate(Max('current_price'))['current_price__max']).replace(' ', '')
    context = {
        'min_price_in_catalog': min_price_in_catalog,
        'max_price_in_catalog': max_price_in_catalog
    }
    return context
