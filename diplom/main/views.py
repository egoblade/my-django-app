from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.db.models import Q, Sum, Avg
from django.utils import timezone
from .models import Category, Product, Review, Order, OrderItem

# Главная
def index(request):
    return render(request, 'main/index/index.html')

# Регистрация
def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:index')
    else:
        form = UserCreationForm()
    return render(request, 'main/auth/register.html', {'form': form})

# Вход
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main:index')
    else:
        form = AuthenticationForm()
    return render(request, 'main/auth/login.html', {'form': form})

# Выход
@login_required
def user_logout(request):
    logout(request)
    return redirect('main:index')

# Категории
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'main/catalog/category_list.html', {'categories': categories})

# Список товаров
def product_list(request, category_id=None):
    category = get_object_or_404(Category, pk=category_id) if category_id else None
    products = Product.objects.filter(available=True)
    if category:
        products = products.filter(category=category)
    return render(request, 'main/catalog/product_list.html', {'category': category, 'products': products})

# Детали товара
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'main/catalog/product_detail.html', {'product': product})

# Поиск
def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = Product.objects.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    return render(request, 'main/catalog/search_results.html', {'query': query, 'results': results})

# Отзыв
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        Review.objects.create(user=request.user, product=product, rating=rating, comment=comment, created_at=timezone.now())
    return redirect('main:product_detail', product_id=product_id)

# Корзина (сессии)
def _get_cart(session):
    return session.setdefault('cart', {})

def add_to_cart(request, product_id):
    cart = _get_cart(request.session)
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session.modified = True
    return redirect('main:cart_detail')

def remove_from_cart(request, product_id):
    cart = _get_cart(request.session)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session.modified = True
    return redirect('main:cart_detail')

def cart_detail(request):
    cart = _get_cart(request.session)
    items, total = [], Decimal('0')
    for pid, qty in cart.items():
        p = get_object_or_404(Product, pk=int(pid))
        subtotal = p.price * qty
        items.append({'product': p, 'quantity': qty, 'subtotal': subtotal})
        total += subtotal
    return render(request, 'main/cart/cart_detail.html', {'items': items, 'total': total})

# Оформление заказа
@login_required
def checkout(request):
    cart = _get_cart(request.session)
    if not cart: return redirect('main:cart_detail')
    items, total = [], Decimal('0')
    for pid, qty in cart.items():
        p = get_object_or_404(Product, pk=int(pid))
        sub = p.price * qty
        items.append({'product': p, 'quantity': qty, 'subtotal': sub})
        total += sub
    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total=total)
        for it in items:
            OrderItem.objects.create(order=order, product=it['product'], quantity=it['quantity'], price=it['product'].price)
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('main:order_success', order_id=order.id)
    return render(request, 'main/order/checkout.html', {'items': items, 'total': total})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'main/order/order_success.html', {'order': order})

# История заказов
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/order/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    items = order.items.all()
    return render(request, 'main/order/order_detail.html', {'order': order, 'items': items})

# Статистика продаж
@login_required
def stats(request):
    if not request.user.is_staff:
        return redirect('main:index')
    orders = Order.objects.filter(status='placed')
    turnover = orders.aggregate(total_sum=Sum('total'))['total_sum'] or 0
    avg_check = orders.aggregate(avg=Avg('total'))['avg'] or 0
    popular = (
        OrderItem.objects.values('product__name')
        .annotate(sold=Sum('quantity'))
        .order_by('-sold')[:5]
    )
    return render(request, 'main/stats.html', {'turnover': turnover, 'avg_check': avg_check, 'popular': popular})