from django.db import models


# Класс Settings — это модель для конфигурации приложения.
class Settings(models.Model):
	title = models.CharField(
		max_length=50,
		verbose_name='Название интернет-магазина',
		help_text='Megano'
	)
	SERVER_EMAIL = models.EmailField(
		max_length=200,
		verbose_name='Сервер электронной почты',
		help_text='test@test.com'
	)
	EMAIL_USE_TLS = models.BooleanField(
		choices=[(True, True), (False, False)],
		verbose_name='Использование шифрования TLS'
	)
	EMAIL_HOST = models.CharField(
		max_length=200,
		verbose_name='Сервер исходящей почты',
		help_text='smtp.test.com'
	)
	EMAIL_PORT = models.IntegerField(
		verbose_name='Порт исходящей почты',
		help_text='587'
	)
	EMAIL_HOST_USER = models.EmailField(
		max_length=200,
		verbose_name='Адрес электронной почты',
		help_text='test@test.com'
	)
	EMAIL_HOST_PASSWORD = models.CharField(
		max_length=200,
		verbose_name='Пароль электронной почты'
	)
	CURRENT_SITE_CURRENCY = models.CharField(
		max_length=1,
		choices=[
			('$', 'Доллар'),
			('€', 'Евро'),
			('₽', 'Рубль')
		],
		verbose_name='Используемая валюта расчетов'
	)
	ALLOWED_HOSTS = models.CharField(
		max_length=100,
		verbose_name='Разрешенный хост',
		help_text='example.com или 0.0.0.0'
	)

	class Meta:
		db_table = 'settings'
		verbose_name = 'настройки сайта'
		verbose_name_plural = 'настройки сайта'

	def __str__(self):
		return self.title
