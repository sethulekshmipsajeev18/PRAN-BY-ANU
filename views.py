from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib import messages
from decimal import Decimal
from django.shortcuts import render, redirect
from .models import Order, Cart, CartItem

import razorpay
from django.conf import settings

from .models import Category, Product, Cart, CartItem, Order

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

from .models import Category, Product

def home(request):
    categories = Category.objects.all()

    return render(request, 'shop/home.html', {
        'categories': categories,
    })

def category(request, pk):
    category = get_object_or_404(Category, id=pk)
    products = Product.objects.filter(category=category, is_sold=False)
    return render(request, 'shop/category.html', {'category': category, 'products': products})

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        try:
            cart = Cart.objects.get(id=cart_id)
        except (Cart.DoesNotExist, TypeError):
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    
    request.session.modified = True # <-- ADD THIS. THIS IS THE KEY
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity = 1 # <-- Always 1. Never 5
    cart_item.save()
    return redirect('cart')


def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product')

    if not cart_items.exists():
        return redirect('cart')

    products = []
    total = 0

    for item in cart_items:
        products.append({
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'subtotal': item.product.price * item.quantity
        })
        total += item.product.price * item.quantity

    context = {
        'products': products,
        'total': total,
    }

    # Customer submitted details
    if request.method == "POST":

        name = request.POST.get('name')
        address = request.POST.get('address')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        razorpay_order = client.order.create({
            'amount': int(total * 100),
            'currency': 'INR',
            'payment_capture': '1'
        })

        context['razorpay_order_id'] = razorpay_order['id']
        context['razorpay_key'] = settings.RAZORPAY_KEY_ID
        context['amount'] = int(total * 100)

        # Keep customer details available to checkout.html
        context['name'] = name
        context['address'] = address
        context['email'] = email
        context['phone'] = phone

        return render(request, 'shop/checkout.html', context)

    return render(request, 'shop/checkout.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})



from django.shortcuts import render
from .models import Order

def payment_success(request):
    name = request.GET.get('name')
    address = request.GET.get('address')
    email = request.GET.get('email')
    phone = request.GET.get('phone')
    total = request.GET.get('total')
    payment_id = request.GET.get('payment_id')

    # SAVE ORDER
    if payment_id:
        Order.objects.create(
            name=name or 'Guest', 
            address=address or '-', 
            email=email or '-', 
            phone=phone or '-', 
            total=total or 0, 
            payment_id=payment_id, 
            status='Ordered'
        )
        # Clear cart
        cart = get_or_create_cart(request)
        cart.items.all().delete()

    # RENDER YOUR BEAUTIFUL THANKYOU PAGE WITH DATA
    return render(request, 'shop/thankyou.html', {
        'name': name, 
        'total': total, 
        'payment_id': payment_id
    })


def orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})

def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/track_order.html', {'order': order})


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For guests - use session to store cart_id
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.filter(id=cart_id, user=None).first()
        else:
            cart = None
        
        if not cart:
            cart = Cart.objects.create(user=None)
            request.session['cart_id'] = cart.id
    return cart


def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = get_or_create_cart(request)  # Use this
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    
    return redirect('cart')

def cart(request):
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)

    # Pran By Anu sells only one piece of each item
    for item in cart_items:
        item.quantity = 1
        item.save()

    total = sum(item.product.price for item in cart_items)

    return render(request, 'shop/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': total
    })


def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)

    cart_item = CartItem.objects.get(
        id=item_id,
        cart=cart
    )

    cart_item.delete()

    return redirect('cart')


from django.shortcuts import render
from .models import Order, Cart
def thankyou(request):
    name = request.GET.get('name', 'Guest')
    address = request.GET.get('address', '-')
    email = request.GET.get('email', '-')
    phone = request.GET.get('phone', '-')
    total = request.GET.get('total', '0')
    payment_id = request.GET.get('payment_id', '')

    if payment_id:
        Order.objects.create(name=name, address=address, email=email, phone=phone, total=float(total), payment_id=payment_id, status='Ordered')
        
        # CLEAR CART
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            cart_id = request.session.get('cart_id')
            cart = Cart.objects.filter(id=cart_id, user=None).first()
            
        if cart:
            cart.items.all().delete()
            if 'cart_id' in request.session:
                del request.session['cart_id']

    return render(request, 'shop/thankyou.html', {'name': name, 'total': total, 'payment_id': payment_id})


def shop(request):
    return render(request, 'shop/shop.html')


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    return render(request, 'shop/contact.html')


from django.db.models import Q


def search(request):

    query = request.GET.get('q', '').strip()

    products = Product.objects.none()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query)
        )

    return render(
        request,
        'shop/search.html',
        {
            'products': products,
            'query': query,
        }
    )