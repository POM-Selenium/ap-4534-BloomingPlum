from django.contrib import admin
from .models import Book
from author.models import Author
from order.models import Order


class AuthorFilter(admin.SimpleListFilter):
    title = 'author'
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        authors = Author.objects.all().order_by('name')
        return [(a.id, f"{a.name} {a.surname}") for a in authors]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(authors__id=self.value())
        return queryset


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'count', 'get_authors')
    list_filter = ('id', 'name', AuthorFilter)
    search_fields = ('id', 'name', 'authors__name', 'authors__surname')
    readonly_fields = ('last_issued',)

    fieldsets = (
        ('Book Information', {
            'fields': ('name', 'description', 'cover', 'year_of_publication')
        }),
        ('Availability', {
            'fields': ('count', 'last_issued')
        }),
    )

    def get_authors(self, obj):
        return ", ".join([f"{a.name} {a.surname}" for a in obj.authors.all()])
    get_authors.short_description = 'Authors'

    def last_issued(self, obj):
        last_order = Order.objects.filter(book=obj).order_by('-created_at').first()
        if last_order:
            return last_order.created_at
        return "Never issued"
    last_issued.short_description = 'Last date of issue'