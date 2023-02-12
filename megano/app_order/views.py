from typing import Any

from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView

from app_order.models import Order, DeliveryType, PaymentMethod, OrderStatus, ProductInOrder
from app_user.forms import SignUpForm


def payment(request: Any, pk: str) -> HttpResponse:
	"""
	Функция отображает шаблон оплаты заказа со своего счета, передавая контекстную переменную идентификатор заказа.

	:param request: Any - объект запроса
	:type request: Any
	:param pk: Первичный ключ заказа
	:type pk: str
	:return: Объект HttpResponse.
	"""
	return render(
		request,
		'app_order/payment.html',
		context={
			'order_pk': pk
		}
	)


def payment_someone(request: Any, pk: str) -> HttpResponse:
	"""
	Функция отображает шаблон оплаты заказа со случайного счета, передавая контекстную переменную идентификатор заказа.

	:param request: Any - объект запроса
	:type request: Any
	:param pk: Первичный ключ заказа
	:type pk: str
	:return: Объект HttpResponse.
	"""
	return render(
		request,
		'app_order/paymentsomeone.html',
		context={
			'order_pk': pk
		}
	)


@transaction.atomic
def progress_payment(request: Any) -> HttpResponse:
	"""
	Принимает запрос, проверяет, четный ли номер карты и не равна ли последняя цифра 0, и если да, то устанавливает
	статус заказа "Оплачен" и устанавливает в поля ошибки платежа значение None. В противном случае он устанавливает
	поля ошибки платежа в соответствующие значения.

	:param request: Объект запроса.
	:type request: Any
	:return: HttpResponse
	"""
	card_number = int(request.POST.get('card_number').replace(' ', ''))
	order = Order.objects.get(id=int(request.POST.get('order_pk')))
	# Проверяем, является ли номер карты четным и не равно ли последнее число 0. Если да, то вычитает количество
	# заказанных товара из количества товара в магазине. Если количество товара после вычета будет меньше 0,
	# устанавливается ошибка платежа и сообщение об ошибке платежа. В противном случае устанавливается статус "Оплачен",
	# убирается ошибки платежа и сообщения об ошибке платежа и сохраняется заказ. Если номер карты не четный или
	#  последнее число равно 0, то устанавливается ошибка платежа и сообщения об ошибке платежа.
	if card_number % 2 == 0 and card_number % 10 != 0:
		for item in order.products_in_order.all():
			item.product.quantity -= item.quantity
			if item.product.quantity < 0:
				order.payment_error = 'Ошибка оплаты'
				order.payment_error_message = 'Товара больше нет в наличии'
				order.save(update_fields=['payment_error', 'payment_error_message'])
			else:
				item.product.save(update_fields=['quantity'])
				order.status_id = 2
				order.payment_error = None
				order.payment_error_message = None
				order.save(update_fields=['status', 'payment_error', 'payment_error_message'])
	else:
		order.payment_error = 'Ошибка оплаты'
		order.payment_error_message = 'Оплата не прошла'
		order.save(update_fields=['payment_error', 'payment_error_message'])
	return render(
		request,
		'app_order/progressPayment.html',
		context={
			'order_pk': order.pk
		}
	)


class OrderView(View):
	"""
	Представление для создания заказа.
	"""

	@classmethod
	def get(cls, request: Any) -> HttpResponse:
		"""
		Функция получает форму для регистрации, тип доставки и способ оплаты. Если пользователь залогинился, то получает
		профиль пользователя, список товаров в корзине и отрисовывает страницу заказа с контекстом в противнос случае
		передает форму для регистрации.

		:param cls: Класс представления
		:param request: Объект запроса.
		:type request: Any
		:return: ответ пользователю.
		"""
		form_signup = SignUpForm()
		delivery_type = DeliveryType.objects.all()
		payment_method = PaymentMethod.objects.all()
		if request.user.id:
			user_profile = request.user.user_profile
			product_list = request.user.user_cart.products_in_carts.all()
			return render(
				request,
				'app_order/order.html',
				context={
					'user_profile': user_profile,
					'delivery_type': delivery_type,
					'payment_method': payment_method,
					'product_list': product_list
				}
			)
		return render(
			request,
			'app_order/order.html',
			context={
				'form_signup': form_signup,
				'delivery_type': delivery_type,
				'payment_method': payment_method
			}
		)

	@classmethod
	def order_confirm(cls, request: Any) -> HttpResponse:
		"""
		Метод отображает шаблон подтверждения заказа

		:param cls: сам класс
		:param request: Любой - объект запроса
		:type request: Any
		:return: Объект HttpResponse.
		"""
		if not request.user.id:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER').split(request.META.get('HTTP_HOST'))[1])
		context = {
			'user': request.user,
			'full_name': request.POST.get('full_name'),
			'phone': request.POST.get('phone'),
			'email': request.POST.get('email'),
			'delivery_type': DeliveryType.objects.get(id=int(request.POST.get('delivery_type'))),
			'city': request.POST.get('city'),
			'address': request.POST.get('address'),
			'payment_method': PaymentMethod.objects.get(id=int(request.POST.get('payment_method'))),
			'product_list': request.user.user_cart.products_in_carts.all(),
			'order_amount': request.user.user_cart.amount
		}
		return render(
			request,
			'app_order/order_confirm.html',
			context=context
		)

	@classmethod
	def order_creation(cls, request: Any) -> HttpResponse:
		"""
		Создает заказ, добавляет товары из корзины в заказ и перенаправляет на страницу оплаты

		:param cls: Класс представления
		:param request: Любой - объект запроса
		:type request: Any
		:return: HttpResponseRedirect
		"""
		order = Order.objects.create(
			user=request.user,
			delivery_type=DeliveryType.objects.get(id=int(request.POST.get('delivery_type'))),
			city=request.POST.get('city'),
			address=request.POST.get('address'),
			payment_method=PaymentMethod.objects.get(id=int(request.POST.get('payment_method'))),
			status=OrderStatus.objects.get(id=1),
			order_amount=request.user.user_cart.amount
		)
		if order.delivery_type.id == 2:
			order.order_amount += order.delivery_type.delivery_cost
		elif order.order_amount < order.delivery_type.purchase_amount_for_free_delivery:
			order.order_amount += order.delivery_type.delivery_cost
		product_list = request.user.user_cart.products_in_carts.all()
		for item in product_list:
			ProductInOrder.objects.create(
				order=order,
				product=item.product,
				quantity=item.quantity,
				price=item.product.current_price
			)
			item.delete()
		if order.payment_method.id == 1:
			return HttpResponseRedirect('/order/payment/%s/' % order.pk)
		else:
			return HttpResponseRedirect('/order/payment_someone/%s/' % order.pk)


class OneOrderDetailView(DetailView):
	"""
	Отображает детальную информацию по заказу. Если пользователь не является владельцем заказа, перенаправит на главную
	страницу.
	:return: Контекст.
	"""
	template_name = 'app_order/oneorder.html'
	model = Order

	def get_context_data(self, **kwargs) -> Any:
		context = super().get_context_data(**kwargs)
		user_order = context['object']
		if user_order.user != self.request.user:
			return HttpResponseRedirect('/')
		context['user_profile'] = self.request.user.user_profile
		context['product_list'] = user_order.products_in_order.all()
		return context
