from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from app_cart.models import Cart, ProductInCart
from app_shop.models import Product


def add_cart(request: Any) -> HttpResponse:
	"""
	Добавляет товар в корзину.

	:param request: Любой - объект запроса.
	:type request: Any
	:return: HttpResponseRedirect (следующий_url)
	"""
	# Получение количества товара из формы и преобразование ее в целое число.
	quantity = int(request.POST.get('amount'))
	# Получение значения id товара из запроса POST.
	product_id = request.POST.get('product_id')
	# Получение id пользователя из запроса POST.
	user_id = request.POST.get('user_id')
	# Получение корзины пользователя.
	# Проверка, авторизован пользователь или нет. Если пользователь не вошел в систему, он получит идентификатор сеанса и
	# использует его для получения корзины.
	if user_id == 'None':
		session_id = request.META.get('CSRF_COOKIE')
		user_cart = Cart.objects.get(session=session_id)
	else:
		user_cart = request.user.user_cart
	product = Product.objects.get(id=product_id)
	# 1. Он пытается получить объект товара в корзине из корзины пользователя.
	# 2. Если товара нет в корзине, вызовется исключение ObjectDoesNotExist.
	# 3. Если товар находится в корзине, добавим количество к существующему количеству и обновим сумму.
	# 4. Если товара нет в корзине, создадим новый объект товара в корзине с товаром, количеством и суммой.
	try:
		product_in_cart = user_cart.products_in_carts.get(product_id=product_id)
		if not product_in_cart:
			raise ObjectDoesNotExist
		product_in_cart.quantity += quantity
		product_in_cart.save(update_fields=['quantity'])
	except ObjectDoesNotExist:
		user_cart.products_in_carts.create(product=product, quantity=quantity)
	# Получение следующего URL-адреса из метода request.POST.get().
	next_url = request.POST.get('next', '/')
	return HttpResponseRedirect(next_url)


class CartView(View):
	"""
	Представления для отображения информации о корзине, составе товаров и методы для изменения состава и количества
	товаров в корзине.
	"""

	@classmethod
	def get(cls, request: Any) -> HttpResponse:
		"""
		Метод получает корзину пользователя.

		:param cls: Класс представления.
		:param request: Любой объект запроса.
		:type request: Any
		:return: ответ на запрос.
		"""
		if not request.user.id:
			session_id = request.META.get('CSRF_COOKIE')
			user_cart = Cart.objects.get(session=session_id)
		else:
			user_cart = Cart.objects.get(user=request.user)
		product_list = user_cart.products_in_carts.all()
		return render(
			request,
			'app_cart/cart.html',
			context={
				'product_list': product_list,
				'cart': user_cart
			}
		)

	@classmethod
	def reduce_quantity(cls, request: Any, **kwargs) -> HttpResponse:
		"""
		Уменьшает количество товара в корзине на единицу.

		:param cls: Класс представления.
		:param request: Объект запроса
		:type request: Any
		:return: ответ на запрос.
		"""
		user_cart = Cart.objects.get(id=kwargs.get('cart'))
		product = ProductInCart.objects.get(id=kwargs.get('product'))
		product.quantity -= 1
		if product.quantity > 0:
			product.save(update_fields=['quantity'])
		else:
			product.delete()
		product_list = user_cart.products_in_carts.all()
		return HttpResponseRedirect('/cart/', {'product_list': product_list, 'cart': user_cart})

	@classmethod
	def increase_quantity(cls, request: Any, **kwargs) -> HttpResponse:
		"""
		Увеличивает количество товара в корзине.

		:param cls: Класс представления.
		:param request: Любой объект запроса.
		:type request: Any
		:return: ответ на запрос.
		"""
		user_cart = Cart.objects.get(id=kwargs.get('cart'))
		product = ProductInCart.objects.get(id=kwargs.get('product'))
		product.quantity += 1
		if product.quantity <= product.product.quantity:
			product.save(update_fields=['quantity'])
		product_list = user_cart.products_in_carts.all()
		return HttpResponseRedirect('/cart/', {
			'product_list': product_list,
			'cart': user_cart
		})

	@classmethod
	def remove_from_cart(cls, request: Any, **kwargs) -> HttpResponse:
		"""
		Удаляет товар из корзины.

		:param cls: Класс представления.
		:param request: Любой объект запроса
		:type request: Any
		:return: ответ на запрос.
		"""
		user_cart = Cart.objects.get(id=kwargs.get('cart'))
		product = ProductInCart.objects.get(id=kwargs.get('product'))
		product.delete()
		product_list = user_cart.products_in_carts.all()
		return HttpResponseRedirect('/cart/', {'product_list': product_list, 'cart': user_cart})

	@classmethod
	def change_quantity(cls, request: Any) -> HttpResponse:
		"""
		Изменяет количество товара в корзине.

		:param cls: Класс представления.
		:param request: Любой объект запроса.
		:type request: Any
		:return: ответ на запрос.
		"""
		user_cart = Cart.objects.get(id=request.POST.get('cart'))
		product = ProductInCart.objects.get(id=request.POST.get('product'))
		product.quantity = int(request.POST.get('amount'))
		if product.quantity == 0:
			product.delete()
		elif product.quantity <= product.product.quantity:
			product.save(update_fields=['quantity'])
		product_list = user_cart.products_in_carts.all()
		return HttpResponseRedirect('/cart/', {
			'product_list': product_list,
			'cart': user_cart
		})
