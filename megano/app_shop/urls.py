from django.urls import path

from app_shop.views import (
	SignUpView,
	LoginView,
	RestorePasswordView,
	LogoutUserView,
	CategoryDetailView,
	SubcategoryDetailView,
	TagDetailView,
	SearchGoodListView,
	add_cart,
	add_review,
	payment,
	payment_someone,
	about,
	AccountView,
	CartView,
	CatalogListView,
	HistoryOrderView,
	IndexView,
	OneOrderDetailView,
	OrderView,
	ProductDetailView,
	ProfileView,
	progress_payment,
	PromotionListView
)

urlpatterns = [
	# Это путь к главной странице.
	path('', IndexView.as_view(), name='index'),
	# Это путь к странице с поиском товаров.
	path('search/', SearchGoodListView.as_view(), name='search'),
	# Это путь к странице добавления товара в корзину.
	path('add_cart/', add_cart, name='add_cart'),
	# Это путь к странице с информацией о магазине.
	path('about/', about, name='about'),
	# Это путь к странице со списком всех товаров со скидками.
	path('sale/', PromotionListView.as_view(), name='sale'),
	# Это путь к странице со списком всех товаров в корзине.
	path('cart/', CartView.as_view(), name='cart'),
	# Это путь к странице уменьшения количества товаров в корзине.
	path('cart/reduce#<int:good>&<int:cart>/', CartView.reduce_quantity, name='reduce_quantity'),
	# Это путь к странице увеличения количества товаров в корзине.
	path('cart/increase#<int:good>&<int:cart>/', CartView.increase_quantity, name='increase_quantity'),
	# Это путь к странице изменения количества товаров в корзине.
	path('cart/change_quantity/', CartView.change_quantity, name='change_quantity'),
	# Это путь на страницу удаления товара из корзины.
	path('cart/remove#<int:good>&<int:cart>/', CartView.remove_from_cart, name='remove_from_cart'),
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
	# Это путь к странице регистрации.
	path('signup/', SignUpView.as_view(), name='signup'),
	# Путь к странице входа в учетную запись.
	path('login/', LoginView.as_view(), name='login'),
	# Это путь к странице для восстановления пароля.
	path('restore_password/', RestorePasswordView.as_view(), name='restore_password'),
	# Путь к странице выхода из учетной записи.
	path('logout/', LogoutUserView.as_view(), name='logout'),
	# Это путь к странице личного кабинета.
	path('account/', AccountView.as_view(), name='account'),
	# Путь к странице изменения личных данных.
	path('profile/', ProfileView.as_view(), name='profile'),
	# Путь к странице истории заказов.
	path('historyorder/', HistoryOrderView.as_view(), name='history_order'),
	# Путь на детальную страницу заказа.
	path('oneorder/<int:pk>/', OneOrderDetailView.as_view(), name='one_order'),
	# Это путь к странице оформления заказа.
	path('order/', OrderView.as_view(), name='order'),
	# Путь к странице подтверждения заказа.
	path('order/order_confirm/', OrderView.order_confirm, name='order_confirm'),
	# Путь на страницу создания заказа.
	path('order/order_creation/', OrderView.order_creation, name='order_creation'),
	# Это путь к платежной странице со своего счета.
	path('payment/<int:pk>/', payment, name='payment'),
	# Это путь к платежной странице со случайного счета.
	path('paymentsomeone/<int:pk>/', payment_someone, name='payment_someone'),
	# Это путь на страницу прогресса оплаты.
	path('progresspayment/', progress_payment, name='progress_payment'),
]
