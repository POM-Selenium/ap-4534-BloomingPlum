from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Book
from author.models import Author
from order.models import Order


@login_required(login_url='/login/')
def book_list(request):
    books = Book.objects.all()

    # Filtering
    title = request.GET.get('title', '').strip()
    author_name = request.GET.get('author', '').strip()

    if title:
        books = books.filter(name__icontains=title)

    if author_name:
        books = books.filter(
            authors__name__icontains=author_name
        ) | books.filter(
            authors__surname__icontains=author_name
        )
        books = books.distinct()

    authors = Author.objects.all()

    return render(request, 'book/book_list.html', {
        'books': books,
        'authors': authors,
        'title_filter': title,
        'author_filter': author_name,
    })


@login_required(login_url='/login/')
def book_detail(request, book_id):
    book = Book.get_by_id(book_id)
    if book is None:
        return render(request, 'book/book_not_found.html')

    book_authors = book.authors.all()
    return render(request, 'book/book_detail.html', {
        'book': book,
        'authors': book_authors,
    })


@login_required(login_url='/login/')
def books_by_user(request, user_id):
    if request.user.role != 1:
        return render(request, 'authentication/access_denied.html')

    from authentication.models import CustomUser
    user = CustomUser.get_by_id(user_id)
    if user is None:
        return render(request, 'authentication/user_not_found.html')

    orders = Order.objects.filter(user=user).select_related('book')
    active_orders = orders.filter(end_at=None)
    returned_orders = orders.exclude(end_at=None)

    return render(request, 'book/books_by_user.html', {
        'profile_user': user,
        'active_orders': active_orders,
        'returned_orders': returned_orders,
    })

@login_required(login_url='/login/')
def add_book(request):
    if request.user.role != 1:
        return render(request, 'authentication/access_denied.html')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        count = request.POST.get('count', 10)
        cover = request.FILES.get('cover')

        # New author fields
        author_name = request.POST.get('author_name', '').strip()
        author_surname = request.POST.get('author_surname', '').strip()

        errors = []
        if not name:
            errors.append('Book title is required.')

        if errors:
            return render(request, 'book/add_book.html', {'errors': errors})

        book = Book(name=name, description=description, count=int(count))
        if cover:
            book.cover = cover
        book.save()

        # Create author and link to book if provided
        if author_name and author_surname:
            author, created = Author.objects.get_or_create(
                name=author_name,
                surname=author_surname,
                defaults={'patronymic': request.POST.get('author_patronymic', '').strip()}
            )
            author.books.add(book)

        return redirect('book:book_detail', book_id=book.id)

    return render(request, 'book/add_book.html')
