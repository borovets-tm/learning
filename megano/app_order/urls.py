from django.urls import path

from app_order.views import OneOrderDetailView, OrderView
from app_order.views import payment, payment_someone, progress_payment


urlpatterns = [
	# Это путь к странице оформления заказа.
	path('', OrderView.as_view(), name='order'),
	# Путь на детальную страницу заказа.
	path('<int:pk>/', OneOrderDetailView.as_view(), name='one_order'),
	# Путь к странице подтверждения заказа.
	path('order_confirm/', OrderView.order_confirm, name='order_confirm'),
	# Путь на страницу создания заказа.
	path('order_creation/', OrderView.order_creation, name='order_creation'),
	# Это путь к платежной странице со своего счета.
	path('payment/<int:pk>/', payment, name='payment'),
	# Это путь к платежной странице со случайного счета.
	path('paymentsomeone/<int:pk>/', payment_someone, name='payment_someone'),
	# Это путь на страницу прогресса оплаты.
	path('progresspayment/', progress_payment, name='progress_payment'),
]
