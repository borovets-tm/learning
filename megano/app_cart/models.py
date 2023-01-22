from django.contrib.auth.models import User
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

	class Meta:
		db_table = 'cart'
		verbose_name = 'корзина'
		verbose_name_plural = 'корзины'

	@property
	def number_of_goods(self) -> int:
		"""
		Если у корзины есть id, то вернуть сумму количества всех товаров в корзине если в корзине есть товары, иначе
		вернуть 0. Если у корзины нет id, вернуть 0.
		:return: Количество товаров в корзине.
		"""
		if self.id:
			if self.goods_in_carts.all():
				return self.goods_in_carts.all().aggregate(Sum('quantity'))['quantity__sum']
			else:
				return 0
		return 0

	@property
	def amount(self) -> int:
		"""
		Если у корзины есть идентификатор, то сложите количество каждого товара в корзине и вернуть общее количество.
		:return: Количество товаров в корзине.
		"""
		if self.id:
			amount = 0
			good_in_cart = self.goods_in_carts.all()
			for good in good_in_cart:
				amount += good.amount
			return amount

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

	class Meta:
		db_table = 'good_in_cart'
		verbose_name = 'товар в корзине'
		verbose_name_plural = 'товары в корзине'

	@property
	def amount(self) -> int:
		"""
		Если id объекта не None, вернуть количество объекта, умноженное на текущую цену товара.
		В противном случае вернуть 0.
		:return: Сумма позиции товаров, исходя из количества и стоимости.
		"""
		if self.id:
			return self.quantity * self.good.current_price
		return 0

	def __str__(self):
		return self.good.title
