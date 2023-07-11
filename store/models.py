from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from django.urls import reverse


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        pass

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(default='', verbose_name='Описание')
    slug = models.SlugField(unique=True, null=True)
    inventory = models.IntegerField(default=0, verbose_name='На складе')
    sold = models.IntegerField(default=0, verbose_name='Продано')
    rating = models.FloatField(default=0, verbose_name='Рэйтинг')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория',
                                 related_name='products')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.slug})

    def get_first_photo(self):
        if self.photos:
            try:
                return self.photos.first().image.url
            except:
                return 'https://themewagon.github.io/vegefoods/images/product-1.jpg'
        else:
            return 'https://themewagon.github.io/vegefoods/images/product-1.jpg'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='products/', verbose_name='Изображение')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Галлерея товаров'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


    @property
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price

    @property
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.title

    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price


    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказах'


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)


    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса доставки'




