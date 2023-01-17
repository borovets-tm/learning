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


class ProfileTabularInLine(admin.TabularInline):
	model = Profile
	fields = ['full_name', 'phone']


admin.site.unregister(User)


@admin.register(User)
class MyUserAdmin(UserAdmin):
	inlines = [ProfileTabularInLine]
	fieldsets = ((None, {'fields': ('username',)}), ('Персональная информация', {'fields': ('email',)}))

	def get_queryset(self, request):
		queryset = super().get_queryset(request)
		return queryset.filter(username=request.user.username)


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
	list_display = ['title']


class SubcategoryTabularInLine(admin.TabularInline):
	model = Subcategory
	fields = ['image_tag', 'title', 'image']
	readonly_fields = ['image_tag']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ['title', 'image_tag']
	inlines = [SubcategoryTabularInLine]


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
	list_display = ['title', 'unit']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ['title']


@admin.register(KeyFeature)
class KeyFeatureAdmin(admin.ModelAdmin):
	list_display = ['list_item']


@admin.register(AddInfo)
class AddInfoAdmin(admin.ModelAdmin):
	list_display = ['list_item']


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
class GoodAdmin(admin.ModelAdmin):
	list_display = ['sku', 'title', 'current_price', 'quantity', 'is_limited', 'image_tag']
	inlines = [
		AddGoodPhotoTabularInline,
		GoodSpecificationTabularInline,
		KeyGoodFeatureTabularInline,
		AddGoodInfoTabularInline,
		GoodTagTabularInline,
		ReviewTabularInline
	]


@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
	list_display = ['title', 'free_delivery']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
	list_display = ['title', 'is_active']


class GoodInOrderTabularInLine(admin.TabularInline):
	model = GoodInOrder
	readonly_fields = ['good', 'price', 'quantity', 'amount']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ['id', 'date_create', 'status', 'city', 'address']
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
	inlines = [GoodInOrderTabularInLine]
	list_filter = ['status']
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

	def mark_as_canceled(self, request, queryset):
		for order in queryset.filter(~Q(status_id=1)):
			for item in order.goods_in_order.all():
				good = item.good
				good.quantity += item.quantity
				good.save(update_fields=['quantity'])
		queryset.update(status_id=10)

	def mark_as_handed_over_to_the_buyer(self, request, queryset):
		queryset.update(status_id=9)

	def mark_as_delivered(self, request, queryset):
		queryset.update(status_id=8)

	def mark_as_on_my_way(self, request, queryset):
		queryset.update(status_id=7)

	def mark_as_sent(self, request, queryset):
		queryset.update(status_id=6)

	def mark_as_assembled(self, request, queryset):
		queryset.update(status_id=5)

	def mark_as_agreed(self, request, queryset):
		queryset.update(status_id=4)

	def mark_as_in_processing(self, request, queryset):
		queryset.update(status_id=3)

	mark_as_canceled.short_description = 'Отменен'
	mark_as_handed_over_to_the_buyer.short_description = 'Вручен покупателю'
	mark_as_delivered.short_description = 'Доставлен'
	mark_as_on_my_way.short_description = 'В пути'
	mark_as_sent.short_description = 'Отправлен'
	mark_as_assembled.short_description = 'Собран'
	mark_as_agreed.short_description = 'Согласован'
	mark_as_in_processing.short_description = 'В обработке'

	def save_form(self, request, form, change):
		pass
