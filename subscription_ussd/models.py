from django.db import models


class Customer(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class LoanProduct(models.Model):
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=255, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual flat rate, percent")
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_term_months = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LoanApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        DISBURSED = "DISBURSED", "Disbursed"
        CLOSED = "CLOSED", "Closed"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="applications")
    product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT, related_name="applications")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    term_months = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - {self.customer.name}"

    @property
    def reference(self):
        return f"MK{self.pk:05d}"
