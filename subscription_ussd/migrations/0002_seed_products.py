from decimal import Decimal

from django.db import migrations

PRODUCTS = [
    ("Salary Advance", "Short-term advance against your monthly salary.", Decimal("15.00"), Decimal("2000000"), 6),
    ("Business Boost", "Working-capital loan for small businesses.", Decimal("18.00"), Decimal("5000000"), 12),
    ("Kilimo Loan", "Seasonal loan for farmers and agribusiness.", Decimal("12.00"), Decimal("3000000"), 9),
    ("Emergency Loan", "Instant small loan for urgent needs.", Decimal("20.00"), Decimal("500000"), 3),
]


def seed(apps, schema_editor):
    LoanProduct = apps.get_model("subscription_ussd", "LoanProduct")
    for name, desc, rate, max_amount, term in PRODUCTS:
        LoanProduct.objects.get_or_create(
            name=name,
            defaults={
                "description": desc,
                "interest_rate": rate,
                "max_amount": max_amount,
                "max_term_months": term,
            },
        )


def unseed(apps, schema_editor):
    LoanProduct = apps.get_model("subscription_ussd", "LoanProduct")
    LoanProduct.objects.filter(name__in=[p[0] for p in PRODUCTS]).delete()


class Migration(migrations.Migration):
    dependencies = [("subscription_ussd", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
