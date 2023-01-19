from typing import Any

from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe


# Возвращает полное имя пользователя.
def get_full_name_user(self: Any) -> str:
	"""
	Функция возвращает полное имя пользователя

	:param self: Любой.
	:type self: Any
	:return: Полное имя пользователя.
	"""
	return self.user_profile.full_name


# Добавление метода отображения пользователя в класс User.
User.add_to_class("__str__", get_full_name_user)


# Класс Profile — это модель, которая хранит в себе расширенную информацию о пользователе
class Profile(models.Model):
	user = models.OneToOneField(
		User,
		on_delete=models.CASCADE,
		verbose_name='пользователь',
		related_name='user_profile'
	)
	phone = models.CharField(
		max_length=10,
		verbose_name='номер телефона',
		help_text='Номер телефона в формате 9998887766'
	)
	full_name = models.CharField(
		null=True,
		blank=True,
		max_length=100,
		verbose_name='полное имя'
	)
	user_photo = models.ImageField(
		null=True,
		blank=True,
		upload_to='profile',
		verbose_name='фото пользователя'
	)

	# Функция, которая возвращает тег изображения для поля user_photo.
	def image_tag(self: Any) -> str:
		"""
		Метод возвращает строку, содержащую HTML-тег изображения.

		:param self: Любой — это объект, который передается функции.
		:type self: Any
		:return: Тег с URL-адресом изображения.
		"""
		return mark_safe('<img src="%s" style="height:30px;" />' % self.user_photo.url)

	image_tag.short_description = 'Image'

	class Meta:
		db_table = 'profile'
		verbose_name = 'профиль пользователя'
		verbose_name_plural = 'профили пользователей'

	def __str__(self):
		return self.user.email
