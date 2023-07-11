from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Category, Product, Order, OrderProduct, ShippingAddress
from django.views.generic import ListView, DetailView
from .forms import LoginForm, RegisterForm, ShippingForm
from django.contrib.auth import login, logout
from django.contrib import messages
from shop import settings
from .utils import CartForAuthenticatedUser
import stripe


# Create your views here.

class MainPageView(ListView):  # product_list.html
    model = Product
    context_object_name = 'products'  # objects
    template_name = 'store/index.html'
    extra_context = {
        'title': 'Home page'
    }


class ShopPageView(ListView):
    model = Product
    paginate_by = 1
    context_object_name = 'products'
    template_name = 'store/shop.html'
    extra_context = {
        'title': 'products',
        'title2': 'PRODUCTS'
    }

    def get_queryset(self):
        category__slug = self.request.GET.get('category')
        if category__slug:
            products = Product.objects.filter(category__slug=category__slug)
            return products
        return Product.objects.all()



def about_view(request):
    return render(request, 'store/about.html')


def contact_view(request):
    return render(request, 'store/contact.html')


def blog_view(request):
    return render(request, 'store/blog.html')


class ProductDetail(DetailView):
    model = Product
    template_name = 'store/product-single.html'
    context_object_name = 'product'


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        products = Product.objects.all()[:4]
        context['products'] = products
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = product.title
        return context


def login_register(request):
    login_form = LoginForm()
    register_form = RegisterForm()

    context = {
        'title': 'Вход или регистрация',
        'login_form': login_form,
        'register_form': register_form
    }
    return render(request, 'store/login_register.html', context)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вход выполнен успешно')
            return redirect('index')
        else:
            messages.error(request, 'Не верные логин или пароль')
            return redirect('login_register')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            # login(request, user)
            messages.success(request, 'Регистрация прошла успешно. Можете авторизоваться')
            return redirect('login_register')
        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text())
            return redirect('login_register')

def user_logout(request):
    logout(request)
    messages.warning(request, 'Вы вышли из аккаунта')
    return redirect('index')


def cart(request):
    if request.user.is_authenticated:
        cart_info = CartForAuthenticatedUser(request).get_cart_info()
        return render(request, 'store/cart.html', cart_info)
    else:
        return redirect('login_register')

def to_cart(request, product_id, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, product_id, action)
        return redirect('cart')
    else:
        return redirect('login_register')


def checkout(request):
    cart_info = CartForAuthenticatedUser(request).get_cart_info()
    cart_info['shipping_form'] = ShippingForm()
    return render(request, 'store/checkout.html', cart_info)


def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()

        shipping_form = ShippingForm(data=request.POST)
        if shipping_form.is_valid():
            address = shipping_form.save(commit=False)
            address.user = request.user
            address.order = cart_info['order']
            address.save()

        total_price = cart_info['cart_total_price']
        total_quantity = cart_info['cart_total_quantity']

        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': or_p.product.title
                },
                'unit_amount': int(or_p.product.price * 100)
            },
            'quantity': or_p.quantity
        } for or_p in cart_info['products']]

        session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )
        return redirect(session.url, 303)


def success(request):
    user_cart = CartForAuthenticatedUser(request)
    user_cart.clear()
    messages.success(request, 'Оплата прошла успешно. Спасибо')
    return render(request, 'store/success.html')
