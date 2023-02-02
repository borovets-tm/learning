from random import sample
from typing import Any

from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import View, DetailView, ListView

from app_cart.models import Cart
from app_order.models import DeliveryType
from app_shop.forms import ReviewForm
from app_shop.models import Product, Subcategory, Category, Tag


def about(request: Any) -> HttpResponse:
	"""
	Функция возвращает обработанный шаблон "О магазине".

	:param request: Это объект запроса, который Django использует для передачи информации из браузера на сервер
	:type request: Any
	:return: Объект HttpResponse.
	"""
	return render(
		request,
		'app_shop/about.html'
	)


def add_review(request: Any, pk: str) -> HttpResponse:
	"""
	Функция принимает запрос и идентификатор продукта, добавляет отзыв о товаре и перенаправляет на страницу продукта.

	:param request: Объект запроса является первым параметром любой функции представления. Он содержит информацию о
	запросе, который был сделан на сервер.
	:type request: Any
	:param pk: Первичный ключ продукта, к которому добавляется отзыв.
	:type pk: str
	:return: HttpResponseRedirect (страница товара) или с формой отзыва.
	"""
	form = ReviewForm(request.POST)
	if form.is_valid():
		form.save()
		return HttpResponseRedirect('/product/%s/' % pk)
	form = ReviewForm()
	return HttpResponseRedirect('/product/%s/' % pk, {'form': form})


# Функция используется всеми представлениями, которые используют шаблон catalog.html.
def sort_of_product(self: Any, context: dict, object_list: Any) -> dict:
	"""
	Сортирует товары по выбранному параметру, обрабатывает фильтры и возвращает контекст с отсортированными и/или
	отфильтрованными товарами.

	:param self: Любой
	:type self: Any
	:param context: словарь переменных контекста, которые будут переданы в шаблон.
	:type context: dict
	:param object_list: список объектов, которые вы хотите разбить на страницы.
	:type object_list: Any
	:return: Словарь.
	"""
	# Установите для переменных number_of_clicks и sort значение по умолчанию.
	number_of_clicks = 0
	sort = None
	# Получение значения нажатой кнопки.
	button = self.request.GET.get('button')
	# Передаем значение нажатой кнопки контексту для дальнейшего использования в случае перехода по пагинатору.
	context['button'] = button
	# Проверяется, есть ли в запросе GET значение для ключей ниже, и если да, то преобразуется его в целое число и
	# присваивается переменным. Если это не так, присваивается 0 переменным.
	context['number_of_clicks_popular'] = 0 if not self.request.GET.get('number_of_clicks_popular') else int(
		self.request.GET.get('number_of_clicks_popular')
	)
	context['number_of_clicks_price'] = 0 if not self.request.GET.get('number_of_clicks_price') else int(
		self.request.GET.get('number_of_clicks_price')
	)
	context['number_of_clicks_novelty'] = 0 if not self.request.GET.get('number_of_clicks_novelty') else int(
		self.request.GET.get('number_of_clicks_novelty')
	)
	context['number_of_clicks_review'] = 0 if not self.request.GET.get('number_of_clicks_review') else int(
		self.request.GET.get('number_of_clicks_review')
	)
	# Получение значения списка активных фильтров из словаря request.GET.
	active_filter = self.request.GET.get('active_filter')
	# Получение номера страницы из запроса.
	page_number = self.request.GET.get('page')
	# Получение требования на сохранение сортировки списка товаров.
	is_non_sorted = self.request.GET.get('non_sorted')
	if active_filter:
		active_filter = active_filter.split(',')
	# Фильтрация товаров по параметрам фильтра.
	if button == 'filter' or active_filter:
		if active_filter:
			title, min_price, max_price, is_availability, is_free_delivery = active_filter
			min_price, max_price = float(min_price), float(max_price)
			context['active_filter'] = active_filter
		else:
			title = self.request.GET.get('title')
			min_price, max_price = list(map(float, self.request.GET.get('price').split(';')))
			is_availability = self.request.GET.get('is_availability')
			is_free_delivery = self.request.GET.get('is_free_delivery')
		context['active_filter'] = '%s,%s,%s,%s,%s' % (title, min_price, max_price, is_availability, is_free_delivery)
		if title:
			object_list = object_list.filter(title__icontains=title)
		else:
			object_list_id = list(item.id for item in object_list if min_price <= item.current_price <= max_price)
			object_list = object_list.filter(id__in=object_list_id)
		if is_availability == 'on':
			object_list.filter(quantity__gt=0)
		if is_free_delivery == 'on':
			min_order = DeliveryType.objects.filter(free_delivery=True).first().purchase_amount_for_free_delivery
			object_list_id = list(item.id for item in object_list if min_order < item.current_price)
			object_list = object_list.filter(id__in=object_list_id)
	# Сортировка товаров по нажатой кнопке.
	if button == 'popularity':
		sort = 'ordered_products__quantity'
		number_of_clicks = context['number_of_clicks_popular'] + (0 if is_non_sorted else 1)
		context['number_of_clicks_popular'] = number_of_clicks
	elif button == 'price':
		sort = 'price'
		number_of_clicks = context['number_of_clicks_price'] + (0 if is_non_sorted else 1)
		context['number_of_clicks_price'] = number_of_clicks
	elif button == 'novelty':
		sort = 'id'
		number_of_clicks = context['number_of_clicks_novelty'] + (0 if is_non_sorted else 1)
		context['number_of_clicks_novelty'] = number_of_clicks
	elif button == 'review':
		sort = 'product_reviews__count'
		number_of_clicks = context['number_of_clicks_review'] + (0 if is_non_sorted else 1)
		context['number_of_clicks_review'] = number_of_clicks
	if sort:
		if number_of_clicks % 2 != 0:
			if button == 'novelty':
				object_list = object_list.order_by('-%s' % sort)
			else:
				object_list = object_list.order_by('%s' % sort)
		else:
			if button == 'novelty':
				object_list = object_list.order_by('%s' % sort)
			else:
				object_list = object_list.order_by('-%s' % sort)
	# Передача обновленных данных контексту.
	context['object_list'] = object_list
	context['min_price'] = str(min(item.current_price for item in object_list))
	context['max_price'] = str(max(item.current_price for item in object_list))
	paginator = Paginator(object_list, 8)
	page_obj = paginator.get_page(page_number)
	context['paginator'] = paginator
	context['page_obj'] = page_obj
	return context


# Это представление, которое отображает Главную страницу.
class IndexView(View):

	@classmethod
	def get(cls, request: Any) -> HttpResponse:
		"""
		Отображает главную страницу магазина.

		:param cls: Класс представления.
		:param request: Любой - объект запроса
		:type request: Any
		:return: ответ на запрос.
		"""
		# Получение токена CSRF из запроса для связки устройства с корзиной.
		session_id = request.META.get('CSRF_COOKIE')
		# Проверка, авторизован пользователь или нет. Если пользователь не вошел в систему, проверяется существование
		# корзины с текущим токеном, если такой корзины не существует, будет создана новая корзина с текущим токеном.
		if not request.user.id:
			if not Cart.objects.filter(session=session_id):
				Cart.objects.create(session=session_id)
		# Получение случайной выборки из 3 категорий из набора запросов категорий.
		categories = Subcategory.objects.annotate(Count('category_products')).filter(category_products__count__gt=0)
		random_number = sample([item.id for item in categories], 3)
		featured_categories = categories.filter(id__in=random_number)
		# Фильтрация товаров по количеству больше 0, затем аннотируется сумма сколько раз заказали товар,
		# а затем упорядочиваются объекты по сумме количества заказанных товаров в порядке убывания.
		popular_product_list = (
			Product.objects.filter(quantity__gt=0)
			.annotate(Sum('ordered_products__quantity'))
			.order_by('-ordered_products__quantity__sum')[:8]
		)
		# Фильтрация товаров по количеству больше 0 и статусу лимитированности версии.
		limited_product_list = Product.objects.filter(quantity__gt=0, is_limited=True)[:16]
		return render(
			request,
			'app_shop/index.html',
			context={
				'featured_categories': featured_categories,
				'popular_product_list': popular_product_list,
				'limited_product_list': limited_product_list
			}
		)


class SearchProductListView(ListView):
	"""
	Представление отображает список объектов результата поиска.
	:return: Контекст.
	"""
	template_name = 'app_shop/catalog.html'
	model = Product

	def get_context_data(self, **kwargs) -> dict:
		context = super().get_context_data(**kwargs)
		query = self.request.GET.get('query')
		object_list = context['object_list'].filter(
			quantity__gt=0,
			title__icontains=query,
		) | Product.objects.filter(
			quantity__gt=0,
			product_tags__tag__title__icontains=query
		)
		tag_list = Tag.objects.filter(title__icontains=query)
		for tag in tag_list:
			if tag.number_of_requests:
				tag.number_of_requests += 1
			else:
				tag.number_of_requests = 1
			tag.save(update_fields=['number_of_requests'])
		context = sort_of_product(self, context, object_list)
		return context


class CategoryDetailView(DetailView):
	"""
	Отображает список товаров в указанной категории.
	:return: Контекст.
	"""
	template_name = 'app_shop/catalog.html'
	model = Category

	def get_context_data(self, **kwargs) -> dict:
		context = super().get_context_data(**kwargs)
		product_in_category = (
			context['object']
			.subcategories
			.values('category_products')
			.filter(~Q(category_products=None))
		)
		object_list = Product.objects.filter(id__in=product_in_category, quantity__gt=0)
		context = sort_of_product(self, context, object_list)
		return context


class SubcategoryDetailView(DetailView):
	"""
	Отображает список товаров в указанной подкатегории.
	:return: Контекст.
	"""
	template_name = 'app_shop/catalog.html'
	model = Subcategory

	def get_context_data(self, **kwargs) -> dict:
		context = super().get_context_data(**kwargs)
		product_in_subcategory = (
			context['object']
			.category_products
			.filter(~Q(quantity=0))
		)
		object_list = Product.objects.filter(id__in=product_in_subcategory)
		context = sort_of_product(self, context, object_list)
		return context


class CatalogListView(ListView):
	"""
	Отображает список всех товаров в магазине.
	:return: Контекст.
	"""
	template_name = 'app_shop/catalog.html'
	model = Product

	def get_context_data(self, **kwargs) -> dict:
		context = super().get_context_data(**kwargs)
		object_list = context['object_list']
		context = sort_of_product(self, context, object_list)
		return context


class TagDetailView(DetailView):
	"""
	Отображает список товаров по тегу.
	:return: Контекст.
	"""
	template_name = 'app_shop/catalog.html'
	model = Tag

	def get_context_data(self, **kwargs) -> dict:
		context = super().get_context_data(**kwargs)
		products_by_tag = context['object'].products_by_tags.filter(product__quantity__gt=0)
		object_list = Product.objects.filter(product_tags__in=products_by_tag, quantity__gt=0)
		context = sort_of_product(self, context, object_list)
		return context


class ProductDetailView(DetailView):
	"""
	Детальная информация о товаре с отзывами о нем.
	:return: Контекст.
	"""
	template_name = 'app_shop/product.html'
	model = Product

	def get_context_data(self, **kwargs) -> dict:
		context = super().get_context_data(**kwargs)
		product = context['object']
		context['specification_list'] = product.product_specifications.all()
		context['key_feature_list'] = product.key_product_features.all()
		context['add_info_list'] = product.add_info_about_product.all()
		try:
			context['review_list'] = product.product_reviews.all()
		except AttributeError:
			context['review_list'] = None
		context['photo_gallery_list'] = product.photo_gallery.all()
		context['tag_list'] = product.product_tags.all()
		if self.request.user.id:
			user_profile = self.request.user.user_profile
			context['form'] = ReviewForm(initial={
				'product': product,
				'email': self.request.user.email,
				'full_name': user_profile.full_name,
				'user_photo': user_profile.user_photo.url if user_profile.user_photo else None
			})
		return context


class PromotionListView(ListView):
	"""
	Отображает список товаров, участвующие в промо акциях.
	:return: Контекст.
	"""
	template_name = 'app_shop/sale.html'
	queryset = Product.objects.filter(~Q(promotion=None)).order_by('promotion__promo_end_date')

	def get_context_data(self, **kwargs) -> dict:
		context = super().get_context_data(**kwargs)
		object_list = context['object_list']
		page_number = self.request.GET.get('page')
		paginator = Paginator(object_list, 8)
		page_obj = paginator.get_page(page_number)
		context['paginator'] = paginator
		context['page_obj'] = page_obj
		return context
