from typing import Any

from django.contrib import admin
from django.db.models import Q

from app_order.models import DeliveryType, Order, ProductInOrder


@admin.register(DeliveryType)
# DeliveryTypeAdmin определяет интерфейс администратора для модели DeliveryType.
class DeliveryTypeAdmin(admin.ModelAdmin):
	list_display = ['title', 'free_delivery']


class ProductInOrderTabularInLine(admin.TabularInline):
	model = ProductInOrder
	readonly_fields = ['product', 'price', 'quantity', 'amount']


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
	inlines = [ProductInOrderTabularInLine]
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
			for item in order.products_in_order.all():
				product = item.product
				product.quantity += item.quantity
				product.save(update_fields=['quantity'])
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
			for item in order.products_in_order.all():
				product = item.product
				product.quantity += item.quantity
				product.save(update_fields=['quantity'])
		super().save_model(request, obj, form, change)
