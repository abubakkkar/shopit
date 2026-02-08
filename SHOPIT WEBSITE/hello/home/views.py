from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string
from decimal import Decimal
import os
import traceback
from .models import (
    Contact, Product, ProductCategory, ProductReview, Order, OrderItem,
    Coupon, UserProfile, Address, Wishlist, SupportTicket, Return
)


def index(request):
    featured_products = Product.objects.filter(is_active=True)[:6]
    categories = ProductCategory.objects.all()
    context = {
        "featured_products": featured_products,
        "categories": categories,
    }
    return render(request, 'index.html', context)


def about(request):
    return render(request, 'about.html')


def services(request):
    return render(request, 'services.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        new_contact = Contact(
            name=name,
            email=email,
            message=message
        )
        new_contact.save()

        return render(request, 'contact.html', {"success": True})

    return render(request, 'contact.html')


def seller(request):
    return render(request, 'seller.html')


def products(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 100000)
    sort_by = request.GET.get('sort', '-created_at')

    products_list = Product.objects.filter(is_active=True)

    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category:
        products_list = products_list.filter(category__name=category)

    try:
        min_price = float(min_price)
        max_price = float(max_price)
        products_list = products_list.filter(price__gte=min_price, price__lte=max_price)
    except:
        pass

    products_list = products_list.order_by(sort_by)

    categories = ProductCategory.objects.all()

    context = {
        'products': products_list,
        'categories': categories,
        'query': query,
        'selected_category': category,
    }
    return render(request, 'products.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    images = product.images.all()
    variants = product.variants.all()
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product_id)[:4]

    if request.user.is_authenticated and request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        review, created = ProductReview.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'images': images,
        'variants': variants,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)


def cart_view(request):
    return render(request, "cart.html")


def checkout(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            payment_method = request.POST.get('payment_method')
            coupon_code = request.POST.get('coupon_code', '')

            cart_data = request.POST.get('cart_data', '{}')
            import json
            cart = json.loads(cart_data)

            order_id = 'ORD-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            discount_amount = 0
            if coupon_code:
                coupon = Coupon.objects.filter(
                    code=coupon_code,
                    is_active=True,
                    valid_from__lte=timezone.now(),
                    valid_till__gte=timezone.now()
                ).first()
                if coupon:
                    discount_amount = coupon.discount_amount
                    coupon.current_uses += 1
                    coupon.save()

            total_amount = Decimal(request.POST.get('total_amount', '0')) - Decimal(discount_amount)

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                order_id=order_id,
                name=name,
                email=email,
                phone=phone,
                address=address,
                total_amount=total_amount,
                payment_method=payment_method,
                discount_amount=discount_amount,
            )

            for product_id, qty in cart.items():
                try:
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        price=product.price
                    )
                    product.stock -= int(qty)
                    product.save()
                except Exception:
                    # continue processing other items but log the issue
                    import traceback
                    print(f"Failed to add product {product_id} to order {order_id}")
                    traceback.print_exc()

            return render(request, 'order_success.html', {'order': order})

        except Exception as e:
            # ensure logs directory exists and write full traceback to a log file
            try:
                os.makedirs('logs', exist_ok=True)
                log_path = os.path.join('logs', 'checkout_errors.log')
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n--- {datetime.now().isoformat()} ---\n")
                    f.write(traceback.format_exc())
                    f.write("\n")
            except Exception:
                # fallback to printing if file logging fails
                print('Failed to write checkout error log:')
                traceback.print_exc()

            user_msg = 'Unexpected server error. Details written to logs/checkout_errors.log'
            return render(request, 'checkout.html', {'error': user_msg})

    return render(request, 'checkout.html')


# Authentication Views
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        login(request, user)
        return redirect('home')

    return render(request, 'register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def dashboard(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    wishlist = Wishlist.objects.get_or_create(user=user)[0]
    addresses = Address.objects.filter(user=user)
    support_tickets = SupportTicket.objects.filter(user=user).order_by('-created_at')

    context = {
        'orders': orders,
        'wishlist': wishlist,
        'addresses': addresses,
        'support_tickets': support_tickets,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    items = order.items.all()
    returns = order.returns.all()

    context = {
        'order': order,
        'items': items,
        'returns': returns,
    }
    return render(request, 'order_detail.html', context)


@login_required(login_url='login')
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(id=product_id).exists():
        wishlist.products.remove(product)
        return JsonResponse({'status': 'removed'})
    else:
        wishlist.products.add(product)
        return JsonResponse({'status': 'added'})


@login_required(login_url='login')
def wishlist_view(request):
    wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
    products = wishlist.products.all()

    context = {'wishlist_products': products}
    return render(request, 'wishlist.html', context)


@login_required(login_url='login')
def save_address(request):
    if request.method == "POST":
        address_type = request.POST.get('address_type')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        Address.objects.create(
            user=request.user,
            address_type=address_type,
            street=street,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )
        return redirect('dashboard')

    return render(request, 'save_address.html')


@login_required(login_url='login')
def create_support_ticket(request):
    if request.method == "POST":
        subject = request.POST.get('subject')
        description = request.POST.get('description')

        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=subject,
            description=description,
        )
        return redirect('ticket_detail', ticket_id=ticket.id)

    return render(request, 'create_ticket.html')


@login_required(login_url='login')
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    messages = ticket.messages.all().order_by('created_at')

    if request.method == "POST":
        message_text = request.POST.get('message')
        from .models import SupportMessage
        SupportMessage.objects.create(
            ticket=ticket,
            user=request.user,
            message=message_text,
        )
        return redirect('ticket_detail', ticket_id=ticket.id)

    context = {'ticket': ticket, 'messages': messages}
    return render(request, 'ticket_detail.html', context)


@login_required(login_url='login')
def request_return(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if request.method == "POST":
        reason = request.POST.get('reason')
        Return.objects.create(order=order, reason=reason)
        return redirect('order_detail', order_id=order_id)

    context = {'order': order}
    return render(request, 'request_return.html', context)


def validate_coupon(request):
    code = request.GET.get('code', '')
    coupon = Coupon.objects.filter(
        code=code,
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_till__gte=timezone.now()
    ).first()

    if coupon:
        return JsonResponse({
            'valid': True,
            'discount_percent': coupon.discount_percent,
            'discount_amount': float(coupon.discount_amount)
        })
    return JsonResponse({'valid': False})
