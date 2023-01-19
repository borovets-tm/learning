from typing import Any

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from app_shop.models import Good


# Класс Cart - это модель, которая хранит в себе информацию о корзине пользователя.
class Cart(models.Model):
	user = models.OneToOneField(
		User,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		verbose_name='пользователь',
		related_name='user_cart'
	)
	session = models.CharField(
		max_length=150,
		verbose_name='ключ сессии'
	)
	amount = models.FloatField(
		null=True,
		blank=True,
		verbose_name='сумма товаров в корзине'
	)
	number_of_goods = models.IntegerField(
		null=True,
		blank=True,
		verbose_name='количество товаров в корзине'
	)

	class Meta:
		db_table = 'cart'
		verbose_name = 'корзина'
		verbose_name_plural = 'корзины'

	def __init__(self: Any, *args, **kwargs) -> None:
		"""
		Обновляет количество товаров и сумму в корзине при добавлении нового товара в корзину.

		:param self: Любой — это экземпляр сохраняемой модели.
		:type self: Any
		"""
		super().__init__(*args, **kwargs)
		try:
			# Проверяем, пуста ли корзина.
			if not self.goods_in_carts:
				raise ObjectDoesNotExist
			# Использование агрегатной функции для суммирования количества всех товаров в корзине.
			self.number_of_goods = self.goods_in_carts.all().aggregate(Sum('quantity'))['quantity__sum']
			# Использование агрегатной функции для суммирования стоимости товаров в корзине.
			self.amount = self.goods_in_carts.all().aggregate(Sum('amount'))['amount__sum']
			# Обновление полей количество товаров и суммы в базе.
			self.save(update_fields=['number_of_goods', 'amount'])
		except ObjectDoesNotExist:
			self.number_of_goods = 0
			self.amount = 0
			self.save(update_fields=['number_of_goods', 'amount'])

	def __str__(self):
		return '%s [user:%s]' % (self.session, self.user)


# Класс GoodInCart - это модель, которая хранит в себе информацию о товарах в корзине.
class GoodInCart(models.Model):
	cart = models.ForeignKey(
		Cart,
		on_delete=models.CASCADE,
		verbose_name='корзина',
		related_name='goods_in_carts'
	)
	good = models.ForeignKey(
		Good,
		on_delete=models.CASCADE,
		verbose_name='товар',
		related_name='added_goods'
	)
	quantity = models.IntegerField(
		verbose_name='количество',
		validators=[MinValueValidator(0)]
	)
	amount = models.FloatField(
		verbose_name='сумма',
		null=True,
		blank=True
	)

	class Meta:
		db_table = 'good_in_cart'
		verbose_name = 'товар в корзине'
		verbose_name_plural = 'товары в корзине'

	def __init__(self: Any, *args, **kwargs) -> None:
		"""
		Если id объекта существует, то рассчитываем сумму товара в корзине.

		:param self: Любой — это экземпляр сохраняемой модели.
		:type self: Any
		"""
		super().__init__(*args, **kwargs)
		if self.id:
			self.amount = self.quantity * self.good.current_price
			self.save(update_fields=['amount'])

	def __str__(self):
		return self.good.title
