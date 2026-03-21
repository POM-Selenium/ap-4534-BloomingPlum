from django.shortcuts import render, redirect
from author.models import Author


def authors_list(request):
    if request.user.role != 1:
        return redirect('/')

    authors = Author.get_all()
    return render(request, 'authors/list.html', {'authors': authors})


def author_create(request):
    if request.user.role != 1:
        return redirect('/')

    if request.method == "POST":
        name = request.POST.get("name")
        surname = request.POST.get("surname")
        patronymic = request.POST.get("patronymic")

        Author.create(name, surname, patronymic)
        return redirect('/authors/')

    return render(request, 'authors/create.html')


def author_delete(request, author_id):
    if request.user.role != 1:
        return redirect('/')

    author = Author.get_by_id(author_id)

    if author and not author.books.exists():
        author.delete()

    return redirect('/authors/')
