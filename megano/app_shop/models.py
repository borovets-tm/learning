from datetime import datetime
from typing import Any

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe


# Класс Category — это модель, которая хранит в себе информацию о категориях товаров.
class Category(models.Model):
	title = models.CharField(
		max_length=50,
		verbose_name='название категории'
	)
	image = models.ImageField(
		upload_to='categories',
		verbose_name='изображение категории'
	)

	def image_tag(self):
		"""
		Метод возвращает строку, содержащую HTML-тег изображения.

		:param self: Любой — это объект, который передается функции.
		:type self: Any
		:return: Тег с URL-адресом изображения.
		"""
		return mark_safe('<img src="%s" style="height:30px;" />' % self.image.url)

	image_tag.short_description = 'Image'

	# Возврат URL-адреса объекта.
	def get_absolute_url(self: Any) -> str:
		"""
		Функция возвращает URL-адрес для доступа к конкретному экземпляру модели.

		:param self: Любой
		:type self: Any
		:return: URL-адрес подробного представления категории товаров.
		"""
		return reverse('category_detail', args=[str(self.id)])

	class Meta:
		db_table = 'category'
		verbose_name = 'категория'
		verbose_name_plural = 'категории'

	def __str__(self):
		return self.title


# Класс Subcategory — это модель, которая хранит в себе информацию о подкатегориях товаров.
class Subcategory(models.Model):
	# Создание отношения внешнего ключа между моделью подкатегории и моделью категории.
	category = models.ForeignKey(
		Category,
		on_delete=models.CASCADE,
		verbose_name='категория',
		related_name='subcategories'
	)
	title = models.CharField(
		max_length=50,
		verbose_name='название подкатегории'
	)
	image = models.ImageField(
		upload_to='categories',
		verbose_name='изображение подкатегории'
	)

	def image_tag(self):
		"""
		Метод возвращает строку, содержащую HTML-тег изображения.

		:param self: Любой — это объект, который передается функции.
		:type self: Any
		:return: Тег с URL-адресом изображения.
		"""
		return mark_safe('<img src="%s" style="height:30px;" />' % self.image.url)

	image_tag.short_description = 'Image'

	# Возврат URL-адреса объекта.
	def get_absolute_url(self: Any) -> str:
		"""
		Функция возвращает URL-адрес для доступа к конкретному экземпляру модели.

		:param self: Любой
		:type self: Any
		:return: URL-адрес подробного представления подкатегории товаров.
		"""
		return reverse('subcategory_detail', args=[str(self.category.id), str(self.id)])

	class Meta:
		db_table = 'subcategory'
		verbose_name = 'подкатегория'
		verbose_name_plural = 'подкатегории'

	def __str__(self):
		return '%s (%s)' % (self.title, self.category)


# Класс Promotion — это модель, которая хранит в себе информацию об акциях в магазине.
class Promotion(models.Model):
	title = models.CharField(
		max_length=100,
		verbose_name='название акции'
	)
	description = models.TextField(
		verbose_name='описание акции'
	)
	is_active = models.BooleanField(
		default=False,
		blank=True,
		null=True,
		verbose_name='статус активности'
	)
	discount_size = models.FloatField(
		validators=[MinValueValidator(0), MaxValueValidator(100)],
		verbose_name='размер скидки'
	)
	promo_start_date = models.DateField(
		blank=True,
		null=True,
		verbose_name='дата начала акции'
	)
	promo_end_date = models.DateField(
		blank=True,
		null=True,
		verbose_name='дата окончания акции',
	)

	class Meta:
		db_table = 'promotion'
		ordering = ['promo_end_date']
		verbose_name = 'акция'
		verbose_name_plural = 'акции'

	def __init__(self, *args, **kwargs):
		"""
		Если promo_end_date меньше сегодняшней даты или promo_start_date больше сегодняшней даты, то акция не активна. В
		противном случае она активен
		"""
		super().__init__(*args, **kwargs)
		if self.id:
			if self.promo_end_date < datetime.today().date() or self.promo_start_date > datetime.today().date():
				self.is_active = False
			else:
				self.is_active = True
			self.save(update_fields=['is_active'])

	# Возврат URL-адреса объекта.
	def get_absolute_url(self: Any) -> str:
		"""
		Функция возвращает URL-адрес для доступа к конкретному экземпляру модели.

		:param self: Любой
		:type self: Any
		:return: URL-адрес подробного представления рекламной акции.
		"""
		return reverse('promotion_detail', args=[str(self.id)])

	def __str__(self):
		return self.title


# Класс DeliveryType — это модель, которая хранит в себе информацию и типе характеристики товара и единице измерения
# характеристики.
class Specification(models.Model):
	title = models.CharField(
		max_length=100,
		verbose_name='название'
	)
	unit = models.CharField(
		max_length=10,
		null=True,
		blank=True,
		verbose_name='единицы измерения'
	)

	class Meta:
		db_table = 'specifications'
		verbose_name = 'характеристика'
		verbose_name_plural = 'характеристики'

	def __str__(self):
		return '%s (%s)' % (self.title, self.unit if self.unit else '-')


# Класс Tag — это модель, которая хранит в себе название тега и количество запросов по данному тегу.
class Tag(models.Model):
	title = models.CharField(
		max_length=20,
		unique=True,
		verbose_name='тег'
	)
	number_of_requests = models.IntegerField(
		default=0,
		null=True,
		blank=True,
		verbose_name='количество запросов по тегу'
	)

	# Возврат URL-адреса объекта.
	def get_absolute_url(self: Any) -> str:
		"""
		Функция возвращает URL-адрес для доступа к конкретному экземпляру модели.

		:param self: Любой
		:type self: Any
		:return: URL-адрес подробного представления тега.
		"""
		return reverse('tag_detail', args=[str(self.id)])

	class Meta:
		db_table = 'tag'
		verbose_name = 'тег'
		verbose_name_plural = 'теги'

	def __str__(self):
		return self.title


# Класс KeyFeature - это модель, которая хранит в себе ключевые особенности товаров.
class KeyFeature(models.Model):
	list_item = models.CharField(
		max_length=100,
		null=False,
		blank=False,
		verbose_name='наименование пункта'
	)
	description = models.TextField(
		null=False,
		blank=False,
		verbose_name='описание'
	)

	class Meta:
		db_table = 'key_feature'
		verbose_name = 'ключевая особенность'
		verbose_name_plural = 'ключевые особенности'

	def __str__(self):
		return self.list_item[:20]


# Класс AddInfo - это модель, которая хранит в себе список значений дополнительной информации о товаре.
class AddInfo(models.Model):
	list_item = models.CharField(
		max_length=50,
		null=False,
		blank=False,
		verbose_name='наименование пункта'
	)

	class Meta:
		db_table = 'add_info'
		verbose_name = 'дополнительная информация'
		verbose_name_plural = 'дополнительная информация'

	def __str__(self):
		return self.list_item[:20]


# Класс Product - это модель, которая хранит в себе информацию о товарах в магазине.
class Product(models.Model):
	category = models.ForeignKey(
		Subcategory,
		on_delete=models.CASCADE,
		verbose_name='категория товара',
		related_name='category_products'
	)
	sku = models.CharField(
		max_length=12,
		null=False,
		blank=False,
		unique=True,
		verbose_name='артикул'
	)
	barcode = models.CharField(
		max_length=15,
		null=False,
		blank=False,
		unique=True,
		verbose_name='штрихкод'
	)
	title = models.CharField(
		max_length=100,
		verbose_name='наименование товара'
	)
	description = models.TextField(
		verbose_name='описание товара'
	)
	price = models.FloatField(
		verbose_name='цена'
	)
	current_price = models.FloatField(
		null=True,
		blank=True,
		verbose_name='текущая цена'
	)
	quantity = models.IntegerField(
		null=False,
		blank=False,
		validators=[MinValueValidator(0)],
		verbose_name='количество товара на складе'
	)
	promotion = models.ForeignKey(
		Promotion,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='products_on_sale',
		verbose_name='участвует в акции'
	)
	main_photo = models.ImageField(
		upload_to='product',
		verbose_name='главное фото товара'
	)
	is_limited = models.BooleanField(
		null=True,
		blank=True,
		default=False,
		verbose_name='ограниченный тираж'
	)

	class Meta:
		db_table = 'product'
		ordering = ['current_price']
		verbose_name = 'товар'
		verbose_name_plural = 'товары'

	def image_tag(self):
		"""
		Метод возвращает строку, содержащую HTML-тег изображения.

		:param self: Любой — это объект, который передается функции.
		:type self: Any
		:return: Тег с URL-адресом изображения.
		"""
		return mark_safe('<img src="%s" style="height:30px;" />' % self.main_photo.url)

	image_tag.short_description = 'Image'

	def __init__(self: Any, *args, **kwargs) -> None:
		"""
		Если у товара есть идентификатор и акция, и акция активна, то текущая цена равна цене минус цена, умноженная на
		размер скидки по акции.

		:param self: Любой — это экземпляр сохраняемой модели.
		:type self: Any
		"""
		super().__init__(*args, **kwargs)
		if self.id:
			if self.promotion:
				if not self.promotion.is_active:
					self.promotion = None
					self.save(update_fields=['promotion'])
			if self.promotion:
				self.current_price = round(self.price - (self.price * self.promotion.discount_size / 100), 0)
			else:
				self.current_price = self.price
			self.save(update_fields=['current_price'])

	# Возврат URL-адреса объекта.
	def get_absolute_url(self: Any) -> str:
		"""
		Функция возвращает URL-адрес для доступа к конкретному экземпляру модели.

		:param self: Любой
		:type self: Any
		:return: URL-адрес подробного представления товара.
		"""
		return reverse('product', args=[str(self.id)])

	def __str__(self):
		return '%s %s %s' % (self.category, self.title, self.current_price)


# Класс AddProductPhoto - это модель, которая хранит в себе дополнительные фотографии товара.
class AddProductPhoto(models.Model):
	product = models.ForeignKey(
		Product,
		on_delete=models.CASCADE,
		related_name='photo_gallery',
		verbose_name='товар'
	)
	photo = models.ImageField(
		upload_to='product_gallery',
		verbose_name='фото товара'
	)

	class Meta:
		db_table = 'add_product_photo'
		verbose_name = 'фотография товара'
		verbose_name_plural = 'фотографии товара'

	def image_tag(self):
		"""
		Метод возвращает строку, содержащую HTML-тег изображения.

		:param self: Любой — это объект, который передается функции.
		:type self: Any
		:return: Тег с URL-адресом изображения.
		"""
		return mark_safe('<img src="%s" style="height:30px;" />' % self.photo.url)

	image_tag.short_description = 'Image'
	image_tag.allow_tags = True


# Класс Review - это модель, которая хранит в себе информацию об отзывах о товаре.
class Review(models.Model):
	product = models.ForeignKey(
		Product,
		on_delete=models.CASCADE,
		verbose_name='товар',
		related_name='product_reviews'
	)
	full_name = models.CharField(
		max_length=100,
		verbose_name='ФИО'
	)
	email = models.EmailField(
		verbose_name='электронная почта'
	)
	user_photo = models.CharField(
		max_length=200,
		null=True,
		blank=True,
		verbose_name='фото пользователя'
	)
	text = models.TextField(
		verbose_name='отзыв'
	)
	creation_date = models.DateTimeField(
		auto_now_add=True,
		verbose_name='дата отзыва'
	)

	class Meta:
		db_table = 'review'
		ordering = ['product']
		verbose_name = 'отзыв на товар'
		verbose_name_plural = 'отзывы на товар'

	def __str__(self):
		return self.product.title


# Класс ProductSpecification - это модель, которая хранит в себе информацию о характеристиках товара.
class ProductSpecification(models.Model):
	product = models.ForeignKey(
		Product,
		on_delete=models.CASCADE,
		verbose_name='товар',
		related_name='product_specifications'
	)
	# Создание внешнего ключа к модели спецификации.
	specification = models.ForeignKey(
		Specification,
		on_delete=models.CASCADE,
		verbose_name='характеристика'
	)
	value = models.CharField(
		max_length=100,
		verbose_name='значение'
	)

	class Meta:
		db_table = 'product_specification'
		verbose_name = 'характеристика товара'
		verbose_name_plural = 'характеристики товаров'

	def __str__(self):
		return '%s: %s - %s' % (self.product.title, self.specification, self.value)


# Класс ProductTag - это модель, которая хранит в себе информацию о тегах товара.
class ProductTag(models.Model):
	product = models.ForeignKey(
		Product,
		on_delete=models.CASCADE,
		verbose_name='товар',
		related_name='product_tags'
	)
	tag = models.ForeignKey(
		Tag,
		on_delete=models.CASCADE,
		verbose_name='тег',
		related_name='products_by_tags'
	)

	class Meta:
		db_table = 'product_tag'
		verbose_name = 'тег товара'
		verbose_name_plural = 'теги товаров'

	def __str__(self):
		return self.tag.title


# Класс KeyProductFeature - это модель, которая хранит в себе информацию о ключевых особенностях товара.
class KeyProductFeature(models.Model):
	product = models.ForeignKey(
		Product,
		on_delete=models.CASCADE,
		related_name='key_product_features',
		verbose_name='товар'
	)
	key_feature = models.ForeignKey(
		KeyFeature,
		on_delete=models.CASCADE,
		related_name='product_with_key_features',
		verbose_name='ключевая особенность'
	)

	class Meta:
		db_table = 'key_product_feature'
		verbose_name = 'ключевая особенность товара'
		verbose_name_plural = 'ключевые особенности товара'

	def __str__(self):
		return '%s (%s)' % (self.key_feature, self.product.title)


# Класс AddProductInfo - это модель, которая хранит в себе информацию о дополнительной информации о товаре.
class AddProductInfo(models.Model):
	product = models.ForeignKey(
		Product,
		on_delete=models.CASCADE,
		verbose_name='товар',
		related_name='add_info_about_product'
	)
	add_info = models.ForeignKey(
		AddInfo,
		on_delete=models.CASCADE,
		verbose_name='наименование пункта'
	)
	value = models.CharField(
		max_length=100,
		verbose_name='значение'
	)

	class Meta:
		db_table = 'add_product_info'
		verbose_name = 'дополнительная информация о товаре'
		verbose_name_plural = 'дополнительные информации о товаре'

	def __str__(self):
		return '%s: %s - %s' % (self.product.title, self.add_info, self.value)
