from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'created_at', 'plated_end_at', 'end_at')
    list_filter = ('created_at', 'end_at')
    search_fields = ('user__email', 'book__name')

    fieldsets = (
        ('Order Details', {
            'fields': ('user', 'book')
        }),
        ('Dates', {
            'fields': ('plated_end_at', 'end_at')
        }),
    )