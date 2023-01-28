from django.urls import path

from app_cart.views import CartView
from app_cart.views import add_cart


urlpatterns = [
	# Это путь к странице со списком всех товаров в корзине.
	path('', CartView.as_view(), name='cart'),
	# Это путь к странице добавления товара в корзину.
	path('add_cart/', add_cart, name='add_cart'),
	# Это путь к странице уменьшения количества товаров в корзине.
	path('reduce#<int:product>&<int:cart>/', CartView.reduce_quantity, name='reduce_quantity'),
	# Это путь к странице увеличения количества товаров в корзине.
	path('increase#<int:product>&<int:cart>/', CartView.increase_quantity, name='increase_quantity'),
	# Это путь к странице изменения количества товаров в корзине.
	path('change_quantity/', CartView.change_quantity, name='change_quantity'),
	# Это путь на страницу удаления товара из корзины.
	path('remove#<int:product>&<int:cart>/', CartView.remove_from_cart, name='remove_from_cart'),
]
