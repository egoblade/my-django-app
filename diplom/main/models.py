from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField('Категория', max_length=100)
    slug = models.SlugField('URL', max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField('Наименование', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    sku = models.CharField('Артикул', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    size = models.CharField('Размер', max_length=50, blank=True)
    width = models.CharField('Ширина', max_length=50, blank=True)
    stock = models.PositiveIntegerField('Остаток')
    available = models.BooleanField('Доступен', default=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

class Review(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар'
    )
    rating = models.PositiveSmallIntegerField('Оценка', choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField('Комментарий')
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    def __str__(self):
        user = self.user.username if self.user else 'Гость'
        return f"Отзыв {self.product.name} от {user}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('placed', 'Оформлен'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='placed')

    def __str__(self):
        return f"Заказ #{self.id} ({self.user.username})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField('Кол-во')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"