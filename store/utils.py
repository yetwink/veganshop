from .models import Order, OrderProduct, Product


class CartForAuthenticatedUser:
    def __init__(self, request, product_id=None, action=None):
        self.user = request.user

        if product_id and action:
            self.add_or_delete(product_id, action)


    def get_cart_info(self):
        order, created = Order.objects.get_or_create(
            user=self.user
        )

        order_products = order.orderproduct_set.all()
        cart_total_quantity = order.get_cart_total_quantity
        cart_total_price = order.get_cart_total_price


        return {
            'cart_total_quantity': cart_total_quantity,
            'cart_total_price': cart_total_price,
            'order': order,
            'products': order_products
        }

    def add_or_delete(self, product_id, action):
        order = self.get_cart_info()['order']
        product = Product.objects.get(pk=product_id)
        order_product, created = OrderProduct.objects.get_or_create(order=order,
                                                                    product=product)
        if action == 'add' and product.inventory > 0:
            order_product.quantity += 1 # +1 в заказе
            product.inventory -= 1 # -1 со склада
        else:
            order_product.quantity -= 1
            product.inventory += 1
        order_product.save()
        product.save()

        if order_product.quantity <= 0:
            order_product.delete()


    def clear(self):
        order = self.get_cart_info()['order']
        order_products = order.orderproduct_set.all()
        for product in order_products:
            product.delete()
        order.save()


