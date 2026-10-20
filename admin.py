from django.contrib import admin
from .models import Category, Product, Order

# 1. FIRST define the OrderAdmin class
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'payment_id')

# 2. THEN register everything
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin) # Now OrderAdmin exists