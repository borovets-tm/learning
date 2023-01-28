from django.contrib import admin

from app_shop.models import (
	Category,
	Subcategory,
	Specification,
	Tag,
	KeyFeature,
	AddInfo,
	Product,
	AddProductPhoto,
	Review,
	ProductSpecification,
	ProductTag,
	KeyProductFeature,
	AddProductInfo,
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


class AddProductPhotoTabularInline(admin.TabularInline):
	model = AddProductPhoto
	fields = ['image_tag', 'photo']
	readonly_fields = ['image_tag']
	classes = ['collapse']


class ProductSpecificationTabularInline(admin.TabularInline):
	model = ProductSpecification
	fields = ['specification', 'value']
	classes = ['collapse']


class KeyProductFeatureTabularInline(admin.TabularInline):
	model = KeyProductFeature
	fields = ['key_feature']
	classes = ['collapse']


class AddProductInfoTabularInline(admin.TabularInline):
	model = AddProductInfo
	fields = ['add_info', 'value']
	classes = ['collapse']


class ProductTagTabularInline(admin.TabularInline):
	model = ProductTag
	fields = ['tag']
	classes = ['collapse']


class ReviewTabularInline(admin.TabularInline):
	model = Review
	fields = ['full_name', 'email', 'text', 'creation_date']
	readonly_fields = ['full_name', 'email', 'text', 'creation_date']
	classes = ['collapse']


@admin.register(Product)
# ProductAdmin определяет интерфейс администратора для модели Product.
class ProductAdmin(admin.ModelAdmin):
	list_display = ['sku', 'title', 'current_price', 'quantity', 'is_limited', 'image_tag']
	autocomplete_fields = ['category']
	inlines = [
		AddProductPhotoTabularInline,
		ProductSpecificationTabularInline,
		KeyProductFeatureTabularInline,
		AddProductInfoTabularInline,
		ProductTagTabularInline,
		ReviewTabularInline
	]


@admin.register(Promotion)
# PromotionAdmin определяет интерфейс администратора для модели Promotion.
class PromotionAdmin(admin.ModelAdmin):
	list_display = ['title', 'promo_start_date', 'promo_end_date']
