from django.contrib import admin
from .models import Customer, LoanProduct, LoanApplication


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "created_at")
    search_fields = ("name", "phone")


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ("name", "interest_rate", "max_amount", "max_term_months", "active")
    list_editable = ("active",)


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer", "product", "amount", "term_months", "status", "amount_paid", "created_at")
    list_filter = ("status", "product")
    search_fields = ("customer__name", "customer__phone")
    list_editable = ("status", "amount_paid")
