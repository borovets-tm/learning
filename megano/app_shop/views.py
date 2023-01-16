from random import sample

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Sum, Q, Min, Max
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.views.generic import View, DetailView, ListView

from app_shop.forms import (
    SignUpForm,
    LoginForm,
    RestorePasswordForm,
    UserProfileUpdate,
    UserDataUpdate,
    ChangePasswordForm,
    ReviewForm
)
from app_shop.models import (
    Profile,
    Cart,
    Good,
    Subcategory,
    Category,
    GoodInCart,
    Tag,
    Order,
    DeliveryType,
    PaymentMethod, OrderStatus, GoodInOrder
)


def add_cart(request):
    quantity = int(request.POST.get('amount'))
    good_id = request.POST.get('good_id')
    user_id = request.POST.get('user_id')
    if user_id == 'None':
        session_id = request.META.get('CSRF_COOKIE')
        user_cart = Cart.objects.get(session=session_id)
    else:
        user_cart = request.user.user_cart
    good = Good.objects.get(id=good_id)
    try:
        good_in_cart = user_cart.goods_in_carts.get(good_id=good_id)
        if not good_in_cart:
            raise ObjectDoesNotExist
        good_in_cart.quantity += quantity
        good_in_cart.amount = good_in_cart.quantity * good.current_price
        good_in_cart.save(update_fields=['quantity', 'amount'])
    except ObjectDoesNotExist:
        user_cart.goods_in_carts.create(good=good, quantity=quantity, amount=quantity*good.current_price)
    next_url = request.POST.get('next', '/')
    return HttpResponseRedirect(next_url)


def add_review(request, pk):
    form = ReviewForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/product/%s/' % pk)
    form = ReviewForm()
    return HttpResponseRedirect('/product/%s/' % pk, {'form': form})


def payment(request, pk):
    return render(
        request,
        'app_shop/payment.html',
        context={
            'order_pk': pk
        }
    )

def payment_someone(request, pk):
    return render(
        request,
        'app_shop/paymentsomeone.html',
        context={
            'order_pk': pk
        }
    )

@transaction.atomic
def progress_payment(request):
    card_number = int(request.POST.get('card_number').replace(' ', ''))
    order = Order.objects.get(id=int(request.POST.get('order_pk')))
    if card_number % 2 == 0 and card_number % 10 != 0:
        order.status_id = 2
        order.payment_error = None
        order.payment_error_message = None
        order.save(update_fields=['status', 'payment_error', 'payment_error_message'])
        for item in order.goods_in_order.all():
            item.good.quantity -= item.quantity
            item.good.save(update_fields=['quantity'])
    else:
        order.payment_error = 'Ошибка оплаты'
        order.payment_error_message = 'Оплата не прошла'
        order.save(update_fields=['payment_error', 'payment_error_message'])
    return render(
        request,
        'app_shop/progressPayment.html',
        context={
            'order_pk': order.pk
        }
    )


def sort_of_good(self, context, object_list):
    button = self.request.GET.get('button')
    context['button'] = button
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
    active_filter = self.request.GET.get('active_filter')
    if active_filter:
        active_filter = active_filter.split(',')
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
            object_list = object_list.filter(current_price__gte=min_price, current_price__lte=max_price)
        if is_availability == 'on':
            object_list.filter(quantity__gt=0)
        if is_free_delivery == 'on':
            min_order = DeliveryType.objects.filter(free_delivery=True).first().purchase_amount_for_free_delivery
            object_list.filter(current_price__gt=min_order)
    if button == 'popularity':
        sort = 'ordered_goods__quantity'
        number_of_clicks = context['number_of_clicks_popular']
        context['number_of_clicks_popular'] += 1
    elif button == 'price':
        sort = 'current_price'
        number_of_clicks = context['number_of_clicks_price']
        context['number_of_clicks_price'] += 1
    elif button == 'novelty':
        sort = 'id'
        number_of_clicks = context['number_of_clicks_novelty']
        context['number_of_clicks_novelty'] += 1
    else:
        sort = 'good_reviews__count'
        number_of_clicks = context['number_of_clicks_review']
        context['number_of_clicks_review'] += 1
    if number_of_clicks % 2 != 0:
        if button == 'novelty':
            object_list = object_list.order_by('%s' % sort)
        else:
            object_list = object_list.order_by('-%s' % sort)
    else:
        if button == 'novelty':
            object_list = object_list.order_by('-%s' % sort)
        else:
            object_list = object_list.order_by('%s' % sort)
    context['object_list'] = object_list
    context['min_price'] = str(object_list.aggregate(Min('current_price'))['current_price__min']).replace(' ', '')
    context['max_price'] = str(object_list.aggregate(Max('current_price'))['current_price__max']).replace(' ', '')
    paginator = Paginator(object_list, 8)
    page_number = self.request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    return context


class IndexView(View):

    @classmethod
    def get(cls, request):
        session_id = request.META.get('CSRF_COOKIE')
        if not request.user.id:
            if not Cart.objects.filter(session=session_id):
                Cart.objects.create(session=session_id)
        categories = (Subcategory
                      .objects.annotate(Count('category_goods'))
                      .filter(category_goods__count__gt=0)
                      )
        random_number = sample([item.id for item in categories], 3)
        featured_categories = categories.filter(id__in=random_number)
        popular_good_list = (
            Good.objects.filter(quantity__gt=0)
            .annotate(Sum('ordered_goods__quantity'))
            .order_by('-ordered_goods__quantity__sum')[:8]
        )
        limited_good_list = Good.objects.filter(quantity__gt=0, is_limited=True)[:16]
        return render(
            request,
            'app_shop/index.html',
            context={
                'featured_categories': featured_categories,
                'popular_good_list': popular_good_list,
                'limited_good_list': limited_good_list
            }
        )


class SearchGoodListView(ListView):
    template_name = 'app_shop/catalog.html'
    model = Good

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        object_list = context['object_list'].filter(
            quantity__gt=0,
            title__icontains=query,
        ) | Good.objects.filter(
            quantity__gt=0,
            good_tags__tag__title__icontains=query
        )
        tag_list = Tag.objects.filter(title__icontains=query)
        for tag in tag_list:
            if tag.number_of_requests:
                tag.number_of_requests += 1
            else:
                tag.number_of_requests = 1
            tag.save(update_fields=['number_of_requests'])
        context = sort_of_good(self, context, object_list)
        return context


class CategoryDetailView(DetailView):
    template_name = 'app_shop/catalog.html'
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        good_in_category = (
            context['object']
            .subcategories
            .values('category_goods')
            .filter(~Q(category_goods=None))
        )
        object_list = Good.objects.filter(id__in=good_in_category, quantity__gt=0)
        context = sort_of_good(self, context, object_list)
        return context


class SubcategoryDetailView(DetailView):
    template_name = 'app_shop/catalog.html'
    model = Subcategory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        good_in_subcategory = (
            context['object']
            .category_goods
            .filter(~Q(quantity=0))
        )
        object_list = Good.objects.filter(id__in=good_in_subcategory)
        context = sort_of_good(self, context, object_list)
        return context


class CatalogListView(ListView):
    template_name = 'app_shop/catalog.html'
    model = Good

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = context['object_list']
        context = sort_of_good(self, context, object_list)
        return context


class TagDetailView(DetailView):
    template_name = 'app_shop/catalog.html'
    model = Tag

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goods_by_tag = context['object'].goods_by_tags.filter(good__quantity__gt=0)
        object_list = Good.objects.filter(good_tags__in=goods_by_tag, quantity__gt=0)
        context = sort_of_good(self, context, object_list)
        return context


class ProductDetailView(DetailView):
    template_name = 'app_shop/product.html'
    model = Good

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        good = context['object']
        context['specification_list'] = good.good_specifications.all()
        context['key_feature_list'] = good.key_good_features.all()
        context['add_info_list'] = good.add_info_about_good.all()
        context['review_list'] = good.product_reviews.all()
        context['photo_gallery_list'] = good.photo_gallery.all()
        context['tag_list'] = good.good_tags.all()
        if self.request.user.id:
            user_profile = self.request.user.user_profile
            context['form'] = ReviewForm(initial={
                'good': good,
                'email': self.request.user.email,
                'full_name': user_profile.full_name,
                'user_photo': user_profile.user_photo.url
            })
        return context


class SignUpView(View):

    @classmethod
    def get(cls, request):
        if request.user.id:
            return HttpResponseRedirect('/')
        next_url = request.META.get('HTTP_REFERER').split(request.META.get('HTTP_HOST'))[1]
        form_signup = SignUpForm()
        return render(
            request,
            'app_shop/signup.html',
            context={
                'form_signup': form_signup,
                'next_url': next_url
            }
        )

    @classmethod
    def post(cls, request):
        if request.user.id:
            return HttpResponseRedirect('/')
        session_id = request.META.get('CSRF_COOKIE')
        form_signup = SignUpForm(request.POST)
        if form_signup.is_valid():
            email = form_signup.cleaned_data.get('email')
            password = form_signup.cleaned_data.get('password1')
            full_name = form_signup.cleaned_data.get('full_name')
            phone = form_signup.cleaned_data.get('phone')
            if User.objects.filter(email=email):
                form_signup.add_error('__all__', 'Пользователь с таким email уже существует!')
                return render(
                    request,
                    'app_shop/signup.html',
                    context={
                        'form_signup': form_signup
                    }
                )
            elif Profile.objects.filter(phone=phone):
                form_signup.add_error('__all__', 'Указанный номер принадлежит другому пользователю')
                return render(
                    request,
                    'app_shop/signup.html',
                    context={
                        'form_signup': form_signup
                    }
                )
            user = User.objects.create_user(username=email, email=email, password=password)
            User.groups.through.objects.create(user_id=user.id, group_id=2)
            Profile.objects.create(user=user, phone=phone, full_name=full_name)
            user_cart = Cart.objects.get(session=session_id)
            user_cart.user = user
            user_cart.session = user.id
            user_cart.save(update_fields=['user', 'session'])
            user = authenticate(username=email, password=password)
            login(request, user)
            if request.POST.get('next_url'):
                return HttpResponseRedirect(request.POST.get('next_url'))
            return HttpResponseRedirect('/')
        else:
            form_signup = SignUpForm()
            return render(
                request,
                'app_shop/signup.html',
                context={
                    'form_signup': form_signup
                }
            )


class LoginView(View):

    @classmethod
    def get(cls, request):
        if request.user.id:
            return HttpResponseRedirect('/')
        next_url = request.META.get('HTTP_REFERER').split(request.META.get('HTTP_HOST'))[1]
        form_login = LoginForm()
        return render(
            request,
            'app_shop/login.html',
            context={
                'form_login': form_login,
                'next_url': next_url
            }
        )

    @classmethod
    def post(cls, request):
        if request.user.id:
            return HttpResponseRedirect('/')
        session_id = request.META.get('CSRF_COOKIE')
        session_cart = Cart.objects.get(session=session_id)
        form_login = LoginForm(request.POST)
        if form_login.is_valid():
            username = form_login.cleaned_data['username']
            password = form_login.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                user_cart = user.user_cart
                if user_cart.goods_in_carts.all() and request.POST.get('next_url') == '/order/':
                    next_url = '/cart/'
                else:
                    next_url = request.POST.get('next_url')
                if session_cart.goods_in_carts.all():
                    for good in session_cart.goods_in_carts.all():
                        if user_cart.goods_in_carts.filter(good=good.good):
                            good_in_cart = user_cart.goods_in_carts.get(good=good.good)
                            good_in_cart.quantity += good.quantity
                            good_in_cart.save(update_fields=['quantity'])
                            good.delete()
                        else:
                            good.cart = user_cart
                            good.save(update_fields=['cart'])
                session_cart.delete()
                if next_url:
                    return HttpResponseRedirect(next_url)
                return HttpResponseRedirect('/')
            else:
                form_login.add_error('__all__', 'Ошибка! Проверьте правильность ввода логина и пароля')
                return render(
                    request,
                    'app_shop/login.html',
                    context={
                        'form_login': form_login
                    }
                )
        else:
            form_login = LoginForm()
            return render(
                request,
                'app_shop/login.html',
                context={
                    'form_login': form_login
                }
            )


class RestorePasswordView(View):

    @classmethod
    def get(cls, request):
        if request.user.id:
            return HttpResponseRedirect('/')
        next_url = request.META.get('HTTP_REFERER').split(request.META.get('HTTP_HOST'))[1]
        form_restore = RestorePasswordForm()
        return render(
            request,
            'app_shop/restore_password.html',
            context={
                'form_restore': form_restore,
                'next_url': next_url
            }
        )

    @classmethod
    def post(cls, request):
        if request.user.id:
            return HttpResponseRedirect('/')
        form_restore = RestorePasswordForm(request.POST)
        if form_restore.is_valid():
            user_email = form_restore.cleaned_data['email']
            new_password = User.objects.make_random_password()
            current_user = User.objects.get(email=user_email)
            if current_user:
                current_user.set_password(new_password)
                current_user.save()
                send_mail(
                    subject='Восстановление пароля',
                    from_email='t.m.borovets@lenta.ru',
                    message='Ваш новый пароль %s. Вы можете изменить его после входа в систему' % new_password,
                    recipient_list=[form_restore.cleaned_data['email']],
                    fail_silently=False
                )
                form_restore.add_error('__all__', 'Письмо с новым паролем было успешно отправлено')
                return render(
                    request,
                    'app_shop/restore_password.html',
                    context={
                        'form_restore': form_restore
                    }
                )
        form_restore.add_error('__all__', 'Пользователь не найден')
        return render(
            request,
            'app_shop/restore_password.html',
            context={
                'form_restore': form_restore
            }
        )


class LogoutUserView(LogoutView):
    next_page = '/'


class AccountView(View):

    @classmethod
    def get(cls, request):
        if not request.user.id:
            return HttpResponseRedirect('/')
        user = request.user
        user_profile = user.user_profile
        order_list = user.user_orders.all()
        return render(
            request,
            'app_shop/account.html',
            context={
                'user': user,
                'user_profile': user_profile,
                'order_list': order_list
            }
        )


class ProfileView(View):

    @classmethod
    def get(cls, request):
        if not request.user.id:
            return HttpResponseRedirect('/')
        user = request.user
        user_profile = user.user_profile
        form_edit_profile = UserProfileUpdate(instance=user_profile)
        form_edit_user = UserDataUpdate(instance=user)
        form_change_pass = ChangePasswordForm(user=user)
        return render(
            request,
            'app_shop/profile.html',
            context={
                'form_edit_profile': form_edit_profile,
                'form_edit_user': form_edit_user,
                'form_change_pass': form_change_pass,
                'user_profile': user_profile,
                'user': user
            }
        )

    @classmethod
    def post(cls, request):
        user = request.user
        user_profile = user.user_profile
        form_edit_profile = UserProfileUpdate(request.POST, request.FILES)
        form_edit_user = UserDataUpdate(request.POST)
        form_change_pass = ChangePasswordForm(request.POST)
        if form_edit_profile.is_valid():
            user_profile.full_name = form_edit_profile.cleaned_data['full_name']
            user_profile.phone = form_edit_profile.cleaned_data['phone']
            user_profile.save(update_fields=['full_name', 'phone'])
            if request.FILES:
                user_profile.user_photo = request.FILES['user_photo']
                user_profile.save(update_fields=['user_photo'])
        if form_edit_user.is_valid():
            user.username = form_edit_user.cleaned_data['email']
            user.email = form_edit_user.cleaned_data['email']
            user.save(update_fields=['username', 'email'])
        if form_change_pass.is_valid():
            user.set_password(raw_password=form_change_pass.new_password1)
        return render(
            request,
            'app_shop/profile.html',
            context={
                'form_edit_profile': form_edit_profile,
                'form_edit_user': form_edit_user,
                'form_change_pass': form_change_pass,
                'user_profile': user_profile,
                'user': user,
                'ok_messages': 'Профиль успешно сохранен'
            }
        )


class HistoryOrderView(View):

    @classmethod
    def get(cls, request):
        if not request.user.id:
            return HttpResponseRedirect('/')
        user = request.user
        order_list = user.user_orders.all()
        return render(
            request,
            'app_shop/historyorder.html',
            context={
                'user': user,
                'order_list': order_list
            }
        )


class OneOrderDetailView(DetailView):
    template_name = 'app_shop/oneorder.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_order = context['object']
        if user_order.user != self.request.user:
            return HttpResponseRedirect('/')
        context['user_profile'] = self.request.user.user_profile
        context['good_list'] = user_order.goods_in_order.all()
        return context


class CartView(View):

    @classmethod
    def get(cls, request):
        if not request.user.id:
            session_id = request.META.get('CSRF_COOKIE')
            user_cart = Cart.objects.get(session=session_id)
        else:
            user_cart = Cart.objects.get(user=request.user)
        good_list = user_cart.goods_in_carts.all()
        return render(
            request,
            'app_shop/cart.html',
            context={
                'good_list': good_list,
                'cart': user_cart
            }
        )

    @classmethod
    def reduce_quantity(cls, request, **kwargs):
        user_cart = Cart.objects.get(id=kwargs.get('cart'))
        good = GoodInCart.objects.get(id=kwargs.get('good'))
        good.quantity -= 1
        if good.quantity > 0:
            good.save(update_fields=['quantity'])
        else:
            good.delete()
        good_list = user_cart.goods_in_carts.all()
        return HttpResponseRedirect('/cart/', {'good_list': good_list, 'cart': user_cart})

    @classmethod
    def increase_quantity(cls, request, **kwargs):
        user_cart = Cart.objects.get(id=kwargs.get('cart'))
        good = GoodInCart.objects.get(id=kwargs.get('good'))
        good.quantity += 1
        if good.quantity <= good.good.quantity:
            good.save(update_fields=['quantity'])
        good_list = user_cart.goods_in_carts.all()
        return HttpResponseRedirect('/cart/', {
            'good_list': good_list,
            'cart': user_cart
        })

    @classmethod
    def remove_from_cart(cls, request, **kwargs):
        user_cart = Cart.objects.get(id=kwargs.get('cart'))
        good = GoodInCart.objects.get(id=kwargs.get('good'))
        good.delete()
        good_list = user_cart.goods_in_carts.all()
        return HttpResponseRedirect('/cart/', {'good_list': good_list, 'cart': user_cart})

    @classmethod
    def change_quantity(cls, request):
        user_cart = Cart.objects.get(id=request.POST.get('cart'))
        good = GoodInCart.objects.get(id=request.POST.get('good'))
        good.quantity = int(request.POST.get('amount'))
        if good.quantity == 0:
            good.delete()
        elif good.quantity <= good.good.quantity:
            good.save(update_fields=['quantity'])
        good_list = user_cart.goods_in_carts.all()
        return HttpResponseRedirect('/cart/', {
            'good_list': good_list,
            'cart': user_cart
        })


class OrderView(View):

    @classmethod
    def get(cls, request):
        print(request.path)
        form_signup = SignUpForm()
        delivery_type = DeliveryType.objects.all()
        payment_method = PaymentMethod.objects.all()
        if request.user.id:
            user_profile = request.user.user_profile
            good_list = request.user.user_cart.goods_in_carts.all()
            return render(
                request,
                'app_shop/order.html',
                context={
                    'user_profile': user_profile,
                    'delivery_type': delivery_type,
                    'payment_method': payment_method,
                    'good_list': good_list
                }
            )
        return render(
            request,
            'app_shop/order.html',
            context={
                'form_signup': form_signup,
                'delivery_type': delivery_type,
                'payment_method': payment_method
            }
        )

    @classmethod
    def order_confirm(cls, request):
        if not request.user.id:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER').split(request.META.get('HTTP_HOST'))[1])
        context = {
            'user': request.user,
            'full_name': request.POST.get('full_name'),
            'phone': request.POST.get('phone'),
            'email': request.POST.get('email'),
            'delivery_type': DeliveryType.objects.get(id=int(request.POST.get('delivery_type'))),
            'city': request.POST.get('city'),
            'address': request.POST.get('address'),
            'payment_method': PaymentMethod.objects.get(id=int(request.POST.get('payment_method'))),
            'good_list': request.user.user_cart.goods_in_carts.all(),
            'order_amount': request.user.user_cart.amount
        }
        return render(
            request,
            'app_shop/order_confirm.html',
            context=context
        )

    @classmethod
    def order_creation(cls, request):
        order = Order.objects.create(
            user=request.user,
            delivery_type=DeliveryType.objects.get(id=int(request.POST.get('delivery_type'))),
            city=request.POST.get('city'),
            address=request.POST.get('address'),
            payment_method=PaymentMethod.objects.get(id=int(request.POST.get('payment_method'))),
            status=OrderStatus.objects.get(id=1),
            order_amount=request.user.user_cart.amount
        )
        if order.delivery_type.id == 2:
            order.order_amount += order.delivery_type.delivery_cost
        elif order.order_amount < order.delivery_type.purchase_amount_for_free_delivery:
            order.order_amount += order.delivery_type.delivery_cost
        good_list = request.user.user_cart.goods_in_carts.all()
        for item in good_list:
            GoodInOrder.objects.create(
                order=order,
                good=item.good,
                quantity=item.quantity,
                price=item.good.current_price,
                amount=item.amount
            )
            item.delete()
        if order.payment_method.id == 1:
            return HttpResponseRedirect('/payment/%s/' % order.pk)
        else:
            return HttpResponseRedirect('/payment_someone/%s/' % order.pk)


def about(request):
    return render(
        request,
        'app_shop/about.html'
    )


def sale(request):
    return render(
        request,
        'app_shop/sale.html'
    )
