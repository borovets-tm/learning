from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from app_cart.models import Cart, GoodInCart
from app_shop.models import Good


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
	good_id = request.POST.get('good_id')
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
	good = Good.objects.get(id=good_id)
	# 1. Он пытается получить объект товара в корзине из корзины пользователя.
	# 2. Если товара нет в корзине, вызовется исключение ObjectDoesNotExist.
	# 3. Если товар находится в корзине, добавим количество к существующему количеству и обновим сумму.
	# 4. Если товара нет в корзине, создадим новый объект товара в корзине с товаром, количеством и суммой.
	try:
		good_in_cart = user_cart.goods_in_carts.get(good_id=good_id)
		if not good_in_cart:
			raise ObjectDoesNotExist
		good_in_cart.quantity += quantity
		good_in_cart.amount = good_in_cart.quantity * good.current_price
		good_in_cart.save(update_fields=['quantity', 'amount'])
	except ObjectDoesNotExist:
		user_cart.goods_in_carts.create(good=good, quantity=quantity, amount=quantity * good.current_price)
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
		good_list = user_cart.goods_in_carts.all()
		return render(
			request,
			'app_cart/cart.html',
			context={
				'good_list': good_list,
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
		good = GoodInCart.objects.get(id=kwargs.get('good'))
		good.quantity -= 1
		if good.quantity > 0:
			good.save(update_fields=['quantity'])
		else:
			good.delete()
		good_list = user_cart.goods_in_carts.all()
		return HttpResponseRedirect('/cart/', {'good_list': good_list, 'cart': user_cart})

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
		good = GoodInCart.objects.get(id=kwargs.get('good'))
		good.quantity += 1
		if good.quantity <= good.good.quantity:
			good.save(update_fields=['quantity'])
		good_list = user_cart.goods_in_carts.all()
		return HttpResponseRedirect('/cart/', {
			'good_list': good_list,
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
		good = GoodInCart.objects.get(id=kwargs.get('good'))
		good.delete()
		good_list = user_cart.goods_in_carts.all()
		return HttpResponseRedirect('/cart/', {'good_list': good_list, 'cart': user_cart})

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
		good = GoodInCart.objects.get(id=request.POST.get('good'))
		good.quantity = int(request.POST.get('amount'))
		if good.quantity == 0:
			good.delete()
		elif good.quantity <= good.good.quantity:
			good.save(update_fields=['quantity'])
		good_list = user_cart.goods_in_carts.all()
		return HttpResponseRedirect('/cart/', {
			'good_list': good_list,
			'cart': user_cart
		})
