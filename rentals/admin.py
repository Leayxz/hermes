from django.contrib import admin
from .models import Car, Rental, Reward, RewardTransaction


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'year', 'daily_rate', 'available']
    list_filter = ['available', 'brand']
    search_fields = ['brand', 'model']


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['id', 'car', 'customer_name', 'customer_email', 'start_date', 'end_date', 'returned']
    list_filter = ['returned', 'start_date']
    search_fields = ['customer_name', 'customer_email']
    date_hierarchy = 'start_date'


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['customer_email', 'total_points', 'tier', 'points_to_next_tier', 'lifetime_points_earned', 'lifetime_points_redeemed', 'updated_at']
    list_filter = ['tier', 'updated_at']
    search_fields = ['customer_email']
    ordering = ['-total_points']


@admin.register(RewardTransaction)
class RewardTransactionAdmin(admin.ModelAdmin):
    list_display = ['customer_email', 'type', 'points', 'rental_id', 'timestamp']
    list_filter = ['type', 'timestamp']
    search_fields = ['customer_email']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
