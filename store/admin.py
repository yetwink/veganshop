from django.contrib import admin
from .models import Product, Category, Gallery
from django.utils.safestring import mark_safe
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'get_product_count']
    prepopulated_fields = {'slug': ['title']}

    def get_product_count(self, obj):
        if obj.products:
            return str(len(obj.products.all()))
        else:
            return '0'

    get_product_count.short_description = 'Кол-во товаров'

class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'inventory', 'price',
                    'sold', 'rating', 'created_at', 'get_photo']
    list_editable = ['inventory', 'price']
    list_display_links = ['title']
    prepopulated_fields = {'slug': ['title']}
    inlines = [GalleryInline]

    def get_photo(self, obj):
        if obj.photos:
            try:
                return mark_safe(f'<img src="{obj.photos.first().image.url}" width="75">')
            except:
                return '-'
        else:
            return '-'

    get_photo.short_description = 'Миниатюра'


