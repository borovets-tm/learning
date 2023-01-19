import json
import os
from typing import Any

import django
from django.conf import settings
from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Q

from app_shop.models import (
	Category,
	Subcategory,
	Specification,
	Tag,
	KeyFeature,
	AddInfo,
	Good,
	AddGoodPhoto,
	Review,
	GoodSpecification,
	GoodTag,
	KeyGoodFeature,
	AddGoodInfo,
	DeliveryType,
	Promotion,
	Settings,
	Profile,
	Order,
	GoodInOrder
)

# Отменяем встроенную регистрацию модели User(AbstractUser)
admin.site.unregister(User)


class ProfileTabularInLine(admin.TabularInline):
	"""
	Класс ProfileTabularInLine создан для подключения к модифицированной версии UserAdmin и связанным управлением учетными
	данными
	"""
	model = Profile
	fields = ['full_name', 'phone']


@admin.register(User)
class MyUserAdmin(UserAdmin):
	"""
	Модификация UserAdmin, для административной панели оставляет для редактирования только логин и электронную почту.
	Также добавляется связанная модель Профиль для изменения связанных данных
	"""
	inlines = [ProfileTabularInLine]
	fieldsets = ((None, {'fields': ('username',)}), ('Персональная информация', {'fields': ('email',)}))

	def get_queryset(self, request: Any) -> Any:
		"""
		Даем возможность администратору управлять только собственными учетными данными.

		:param request: Объект запроса.
		:type request: Any
		:return: Набор запросов фильтруется по имени пользователя, вошедшего в систему.
		"""
		queryset = super().get_queryset(request)
		return queryset.filter(username=request.user.username)


@admin.register(Settings)
# SettingsAdmin определяет интерфейс администратора для модели Settings.
class SettingsAdmin(admin.ModelAdmin):
	list_display = ['title']

	def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
		settings_file = os.path.join(settings.BASE_DIR, 'settings.json')
		data = {
			'ALLOWED_HOSTS': obj.ALLOWED_HOSTS,
			'SERVER_EMAIL': obj.SERVER_EMAIL,
			'EMAIL_USE_TLS': obj.EMAIL_USE_TLS,
			'EMAIL_HOST': obj.EMAIL_HOST,
			'EMAIL_PORT': obj.EMAIL_PORT,
			'EMAIL_HOST_USER': obj.EMAIL_HOST_USER,
			'EMAIL_HOST_PASSWORD': obj.EMAIL_HOST_PASSWORD
		}
		with open(settings_file, 'w') as file:
			json.dump(data, file, indent=4)
		super().save_model(request, obj, form, change)


class SubcategoryTabularInLine(admin.TabularInline):
	model = Subcategory
	fields = ['image_tag', 'title', 'image']
	readonly_fields = ['image_tag']


@admin.register(Category)
# CategoryAdmin определяет интерфейс администратора для модели Category.
class CategoryAdmin(admin.ModelAdmin):
	list_display = ['title', 'image_tag']
	inlines = [SubcategoryTabularInLine]


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
	list_display = ['title', 'unit']

	def get_model_perms(self, request):
		"""
		Возврат пустого словаря разрешений, таким образом скрываем модель от индекса администратора.
		"""
		return {}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ['title']

	def get_model_perms(self, request):
		"""
		Возврат пустого словаря разрешений, таким образом скрываем модель от индекса администратора.
		"""
		return {}


@admin.register(Subcategory)
# Нужен для того чтобы работал поиск по категориям в выпадающем списке при создании нового товара.
class SubcategoryAdmin(admin.ModelAdmin):
	search_fields = ['title']

	def get_model_perms(self, request):
		"""
		Возврат пустого словаря разрешений, таким образом скрываем модель от индекса администратора.
		"""
		return {}


@admin.register(KeyFeature)
class KeyFeatureAdmin(admin.ModelAdmin):
	list_display = ['list_item']

	def get_model_perms(self, request):
		"""
		Возврат пустого словаря разрешений, таким образом скрываем модель от индекса администратора.
		"""
		return {}


@admin.register(AddInfo)
class AddInfoAdmin(admin.ModelAdmin):
	list_display = ['list_item']

	def get_model_perms(self, request):
		"""
		Возврат пустого словаря разрешений, таким образом скрываем модель от индекса администратора.
		"""
		return {}


class AddGoodPhotoTabularInline(admin.TabularInline):
	model = AddGoodPhoto
	fields = ['image_tag', 'photo']
	readonly_fields = ['image_tag']


class GoodSpecificationTabularInline(admin.TabularInline):
	model = GoodSpecification
	fields = ['specification', 'value']


class KeyGoodFeatureTabularInline(admin.TabularInline):
	model = KeyGoodFeature
	fields = ['key_feature']


class AddGoodInfoTabularInline(admin.TabularInline):
	model = AddGoodInfo
	fields = ['add_info', 'value']


class GoodTagTabularInline(admin.TabularInline):
	model = GoodTag
	fields = ['tag']


class ReviewTabularInline(admin.TabularInline):
	model = Review
	fields = ['full_name', 'email', 'text', 'creation_date']
	readonly_fields = ['full_name', 'email', 'text', 'creation_date']


@admin.register(Good)
# GoodAdmin определяет интерфейс администратора для модели Good.
class GoodAdmin(admin.ModelAdmin):
	list_display = ['sku', 'title', 'current_price', 'quantity', 'is_limited', 'image_tag']
	autocomplete_fields = ['category']
	inlines = [
		AddGoodPhotoTabularInline,
		GoodSpecificationTabularInline,
		KeyGoodFeatureTabularInline,
		AddGoodInfoTabularInline,
		GoodTagTabularInline,
		ReviewTabularInline
	]


@admin.register(DeliveryType)
# DeliveryTypeAdmin определяет интерфейс администратора для модели DeliveryType.
class DeliveryTypeAdmin(admin.ModelAdmin):
	list_display = ['title', 'free_delivery']


@admin.register(Promotion)
# PromotionAdmin определяет интерфейс администратора для модели Promotion.
class PromotionAdmin(admin.ModelAdmin):
	list_display = ['title', 'is_active']


class GoodInOrderTabularInLine(admin.TabularInline):
	model = GoodInOrder
	readonly_fields = ['good', 'price', 'quantity', 'amount']


@admin.register(Order)
# OrderAdmin определяет интерфейс администратора для модели Order.
class OrderAdmin(admin.ModelAdmin):
	# Список полей, которые будут отображаться в интерфейсе администратора.
	list_display = ['id', 'date_create', 'status', 'city', 'address']
	# Делаем поля только для чтения в админке.
	readonly_fields = [
		'date_create',
		'city',
		'address',
		'payment_method',
		'delivery_type',
		'user',
		'payment_error',
		'payment_error_message',
		'order_amount'
	]
	# Способ группировки полей в панели администратора.
	fieldsets = (
		(
			None, {
				'fields': (
					'status',
					'user',
					'date_create',
					'order_amount',
				)
			}
		),
		(
			'Информация о доставке', {
				'fields': (
					'delivery_type',
					'city',
					'address',
				)
			}
		),
		(
			'Информация об оплате', {
				'fields': (
					'payment_method',
					'payment_error',
					'payment_error_message',
				)
			}
		)
	)
	# Добавление Товаров в заказе для администрирования в интерфейс OrderAdmin.
	inlines = [GoodInOrderTabularInLine]
	# Список добавляет боковую панель фильтра, которая позволяет фильтровать список изменений по полю статуса.
	list_filter = ['status']
	# Список действий, которые можно выполнить над выбранными заказами.
	actions = [
		'mark_as_in_processing',
		'mark_as_agreed',
		'mark_as_assembled',
		'mark_as_sent',
		'mark_as_on_my_way',
		'mark_as_delivered',
		'mark_as_handed_over_to_the_buyer',
		'mark_as_canceled'
	]

	def mark_as_canceled(self, request: Any, queryset: Any) -> None:
		"""
		Метод принимает набор заказов и помечает их как отмененные, возвращая товары в магазин если заказ находился не
		в статусе "Не оплачен".

		:param request: Объект запроса.
		:type request: Any
		:param queryset: Набор запросов объектов, выбранных в админке.
		:type queryset: Any
		"""
		for order in queryset.filter(~Q(status_id=1)):
			for item in order.goods_in_order.all():
				good = item.good
				good.quantity += item.quantity
				good.save(update_fields=['quantity'])
		queryset.update(status_id=10)

	def mark_as_handed_over_to_the_buyer(self, request: Any, queryset: Any) -> None:
		"""
		Обновляет статус выбранных заказов на «Вручен покупателю».

		:param request: Объект запроса.
		:type request: Any
		:param queryset: Набор запросов объектов, выбранных на странице списка изменений.
		:type queryset: Any
		"""
		queryset.update(status_id=9)

	def mark_as_delivered(self, request: Any, queryset: Any) -> None:
		"""
		Обновляет статус выбранных заказов на «Доставлен».

		:param request: Объект запроса.
		:type request: Any
		:param queryset: Набор запросов объектов, выбранных на странице списка изменений.
		:type queryset: Any
		"""
		queryset.update(status_id=8)

	def mark_as_on_my_way(self, request: Any, queryset: Any) -> None:
		"""
		Обновляет статус выбранных заказов на «В пути».

		:param request: Объект запроса.
		:type request: Any
		:param queryset: Набор запросов объектов, выбранных на странице списка изменений.
		:type queryset: Any
		"""
		queryset.update(status_id=7)

	def mark_as_sent(self, request: Any, queryset: Any) -> None:
		"""
		Обновляет статус выбранных заказов на «Отправлен».

		:param request: Объект запроса.
		:type request: Any
		:param queryset: Набор запросов объектов, выбранных на странице списка изменений.
		:type queryset: Any
		"""
		queryset.update(status_id=6)

	def mark_as_assembled(self, request: Any, queryset: Any) -> None:
		"""
		Обновляет статус выбранных заказов на «Собран».

		:param request: Объект запроса.
		:type request: Any
		:param queryset: Набор запросов объектов, выбранных на странице списка изменений.
		:type queryset: Any
		"""
		queryset.update(status_id=5)

	def mark_as_agreed(self, request: Any, queryset: Any) -> None:
		"""
		Обновляет статус выбранных заказов на «Согласован».

		:param request: Объект запроса.
		:type request: Any
		:param queryset: Набор запросов объектов, выбранных на странице списка изменений.
		:type queryset: Any
		"""
		queryset.update(status_id=4)

	def mark_as_in_processing(self, request: Any, queryset: Any) -> None:
		"""
		Обновляет статус выбранных заказов на «В обработке».

		:param request: Объект запроса.
		:type request: Any
		:param queryset: Набор запросов объектов, выбранных на странице списка изменений.
		:type queryset: Any
		"""
		queryset.update(status_id=3)

	mark_as_canceled.short_description = 'Отменен'
	mark_as_handed_over_to_the_buyer.short_description = 'Вручен покупателю'
	mark_as_delivered.short_description = 'Доставлен'
	mark_as_on_my_way.short_description = 'В пути'
	mark_as_sent.short_description = 'Отправлен'
	mark_as_assembled.short_description = 'Собран'
	mark_as_agreed.short_description = 'Согласован'
	mark_as_in_processing.short_description = 'В обработке'

	def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
		"""
		Если статус заказа не "Не оплачен" и статус изменился на "Отменен", то к количеству товара на складе добавляется
		количество товара в заказе

		:param request: Текущий объект запроса.
		:type request: Any
		:param obj: Редактируемый объект.
		:type obj: Any
		:param form: Экземпляр формы, который использовался для проверки данных.
		:type form: Any
		:param change: True, если объект изменяется, и False, если он добавляется.
		:type change: Any
		"""
		order = Order.objects.get(id=obj.id)
		if order.status.id != 1 and request.POST['status'] == '10':
			for item in order.goods_in_order.all():
				good = item.good
				good.quantity += item.quantity
				good.save(update_fields=['quantity'])
		super().save_model(request, obj, form, change)
