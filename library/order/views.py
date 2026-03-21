from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

from order.models import Order
from book.models import Book


@login_required
def orders_list(request):
    if request.user.role == 1:
        orders = Order.get_all()
    else:
        orders = Order.objects.filter(user=request.user)

    return render(request, 'orders/list.html', {'orders': orders})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user, end_at=None)
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def create_order(request):
    books = Book.get_all()

    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        plated_end_at = request.POST.get('plated_end_at')

        book = Book.get_by_id(book_id)

        if not book:
            messages.error(request, 'Book not found.')
            return redirect('/orders/create/')

        if book.count <= 0:
            messages.error(request, 'This book is out of stock.')
            return redirect('/orders/create/')

        Order.create(request.user, book, plated_end_at)
        book.count -= 1
        book.save()

        messages.success(request, 'Order created successfully.')
        return redirect('/orders/')

    return render(request, 'orders/create.html', {'books': books})


@login_required
def close_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if order.user != request.user and request.user.role != 1:
        messages.error(request, 'You cannot close this order.')
        return redirect('/orders/')

    if order.end_at is None:
        order.end_at = timezone.now()
        order.save()

        book = order.book
        if book:
            book.count += 1
            book.save()

        messages.success(request, 'Order closed successfully.')

    return redirect('/orders/')