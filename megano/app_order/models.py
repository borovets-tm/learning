from typing import Any

from django.contrib.auth.models import User
from django.db import models

from app_shop.models import Good


# Класс OrderStatus — это модель, которая хранит в себе список статусов заказа.
class OrderStatus(models.Model):
	title = models.CharField(
		max_length=30,
		verbose_name='статус заказа'
	)

	class Meta:
		db_table = 'order_status'
		verbose_name = 'статус заказа'
		verbose_name_plural = 'статусы заказов'

	def __str__(self):
		return self.title


# Класс DeliveryType — это модель, которая хранит в себе доступные варианты доставки.
class DeliveryType(models.Model):
	title = models.CharField(
		max_length=30,
		verbose_name='тип доставки'
	)
	free_delivery = models.BooleanField(
		null=True,
		blank=True,
		default=False,
		choices=((True, 'Доступна'), (False, 'Недоступна'),),
		verbose_name='возможность бесплатной доставки'
	)
	purchase_amount_for_free_delivery = models.IntegerField(
		verbose_name='минимальная сумма заказа для бесплатной доставки',
		null=True,
		blank=True
	)
	delivery_cost = models.IntegerField(
		verbose_name='стоимость платной доставки'
	)

	class Meta:
		db_table = 'delivery_type'
		verbose_name = 'тип доставки'
		verbose_name_plural = 'типы доставки'

	def __str__(self):
		return self.title


# Класс PaymentMethod — это модель, которая хранит в себе доступные варианты оплаты.
class PaymentMethod(models.Model):
	title = models.CharField(
		max_length=30,
		verbose_name='способ оплаты'
	)

	class Meta:
		db_table = 'payment_method'
		verbose_name = 'способ оплаты'
		verbose_name_plural = 'способы оплаты'

	def __str__(self):
		return self.title


# Класс Order - это модель, которая хранит в себе информацию о заказах покупателей.
class Order(models.Model):
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='user_orders',
		verbose_name='пользователь'
	)
	date_create = models.DateTimeField(
		auto_now_add=True,
		verbose_name='дата заказа'
	)
	delivery_type = models.ForeignKey(
		DeliveryType,
		on_delete=models.CASCADE,
		verbose_name='тип доставки',
		related_name='orders_with_delivery_type'
	)
	city = models.CharField(
		max_length=100,
		verbose_name='город доставки'
	)
	address = models.TextField(
		verbose_name='адрес доставки'
	)
	payment_method = models.ForeignKey(
		PaymentMethod,
		on_delete=models.CASCADE,
		verbose_name='способ оплаты',
		related_name='orders_with_payment_method'
	)
	status = models.ForeignKey(
		OrderStatus,
		on_delete=models.CASCADE,
		default=1,
		verbose_name='статус заказ',
		related_name='orders_with_status'
	)
	payment_error = models.CharField(
		max_length=50,
		null=True,
		blank=True,
		verbose_name='ошибка при оплате'
	)
	payment_error_message = models.CharField(
		max_length=200,
		null=True,
		blank=True,
		verbose_name='сообщение об ошибке при оплате'
	)
	order_amount = models.FloatField(
		verbose_name='сумма заказа',
		blank=True,
		null=True,
	)

	class Meta:
		db_table = 'order'
		ordering = ['-date_create']
		verbose_name = 'заказ'
		verbose_name_plural = 'заказы'

	def __str__(self):
		return '№%(id)s | %(date)s - %(status)s' % {
			'id': self.id,
			'date': self.date_create.strftime('%d.%m.%Y - %H:%M:%S'),
			'status': self.status
		}


# Класс GoodInOrder - это модель, которая хранит в себе информацию о товарах в заказе.
class GoodInOrder(models.Model):
	order = models.ForeignKey(
		Order,
		null=True,
		on_delete=models.SET_NULL,
		verbose_name='заказ',
		related_name='goods_in_order'
	)
	good = models.ForeignKey(
		Good,
		on_delete=models.CASCADE,
		verbose_name='товар',
		related_name='ordered_goods'
	)
	price = models.FloatField(
		verbose_name='цена товара'
	)
	quantity = models.IntegerField(
		verbose_name='количество'
	)

	class Meta:
		db_table = 'good_in_order'
		verbose_name = 'товар в заказе'
		verbose_name_plural = 'товары в заказе'

	@property
	def amount(self) -> float:
		"""
		Если идентификатор объекта не равен None, вернуть количество, умноженное на цену, иначе вернуть 0
		:return: Сумма позиции товара, исходя из его количества.
		"""
		if self.id:
			return self.quantity * self.price
		return 0

	def __str__(self):
		return self.good.title
