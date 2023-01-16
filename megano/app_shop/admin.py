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
    DeliveryType,
    Promotion
)


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
