from django.contrib import admin

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
	Promotion,
)


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


@admin.register(Promotion)
# PromotionAdmin определяет интерфейс администратора для модели Promotion.
class PromotionAdmin(admin.ModelAdmin):
	list_display = ['title', 'is_active']
