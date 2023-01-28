from django.urls import path

from app_shop.views import (
	CategoryDetailView,
	SubcategoryDetailView,
	TagDetailView,
	SearchProductListView,
	add_review,
	about,
	CatalogListView,
	IndexView,
	ProductDetailView,
	PromotionListView
)

urlpatterns = [
	# Это путь к главной странице.
	path('', IndexView.as_view(), name='index'),
	# Это путь к странице с поиском товаров.
	path('search/', SearchProductListView.as_view(), name='search'),
	# Это путь к странице с информацией о магазине.
	path('about/', about, name='about'),
	# Это путь к странице со списком всех товаров со скидками.
	path('sale/', PromotionListView.as_view(), name='sale'),
	# Это путь на страницу со списком всех товаров.
	path('catalog/', CatalogListView.as_view(), name='catalog'),
	# Это путь на страницу со списком товаров в категории.
	path('category/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
	# Это путь на страницу со списком товаров в подкатегории.
	path('category/<int:category>/<int:pk>/', SubcategoryDetailView.as_view(), name='subcategory_detail'),
	# Это путь к странице со списком товаров по тегу.
	path('tag/<int:pk>/', TagDetailView.as_view(), name='tag_detail'),
	# Это путь к странице сведений о товаре.
	path('product/<int:pk>/', ProductDetailView.as_view(), name='product'),
	# Это путь к странице добавления отзыва о товаре.
	path('product/<int:pk>/add_review/', add_review, name='add_review'),
]
