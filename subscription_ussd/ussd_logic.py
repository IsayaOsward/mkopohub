from decimal import Decimal, InvalidOperation

from .models import Customer, LoanApplication, LoanProduct


def con(text):
    return f"CON {text}"


def end(text):
    return f"END {text}"


def _money(amount):
    return f"TZS {amount:,.0f}"


def _active_products():
    return list(LoanProduct.objects.filter(active=True).order_by("id"))


def _product_list(products):
    return "\n".join(f"{i + 1}. {p.name}" for i, p in enumerate(products))


def _parse_amount(raw):
    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError):
        return None


def _schedule(product, amount, term_months):
    interest = amount * product.interest_rate / Decimal(100) * Decimal(term_months) / Decimal(12)
    total = amount + interest
    monthly = total / Decimal(term_months)
    return total, monthly


def _main_menu(name):
    return con(
        f"Welcome {name}!\n"
        "1. Apply for a loan\n"
        "2. Check application status\n"
        "3. Loan products\n"
        "4. Repayment info"
    )


def _apply(customer, rest):
    products = _active_products()
    if not products:
        return end("No loan products available right now.")

    if not rest:
        return con(f"Select a loan product:\n{_product_list(products)}")

    choice = rest[0]
    if not (choice.isdigit() and 1 <= int(choice) <= len(products)):
        return con(f"Invalid choice.\nSelect a loan product:\n{_product_list(products)}")
    product = products[int(choice) - 1]

    if len(rest) == 1:
        return con(
            f"{product.name}\nRate: {product.interest_rate}% p.a.\n"
            f"Max: {_money(product.max_amount)}\nEnter amount to borrow:"
        )

    amount = _parse_amount(rest[1])
    if amount is None or amount <= 0:
        return con(f"Invalid amount.\nEnter amount to borrow (max {_money(product.max_amount)}):")
    if amount > product.max_amount:
        return con(f"Max is {_money(product.max_amount)}.\nEnter amount to borrow:")

    if len(rest) == 2:
        return con(f"Enter repayment period in months (max {product.max_term_months}):")

    term_raw = rest[2]
    if not (term_raw.isdigit() and 1 <= int(term_raw) <= product.max_term_months):
        return con(f"Invalid period.\nEnter repayment period in months (max {product.max_term_months}):")
    term = int(term_raw)

    total, monthly = _schedule(product, amount, term)
    if len(rest) == 3:
        return con(
            f"Confirm application:\n{product.name}\nAmount: {_money(amount)}\n"
            f"Period: {term} months\nTotal due: {_money(total)}\nMonthly: {_money(monthly)}\n"
            "1. Confirm\n2. Cancel"
        )

    decision = rest[3]
    if decision == "1":
        app = LoanApplication.objects.create(
            customer=customer, product=product, amount=amount, term_months=term
        )
        return end(
            f"Application {app.reference} submitted.\n"
            f"Amount: {_money(amount)}\nStatus: {app.get_status_display()}.\n"
            "You will be notified."
        )
    if decision == "2":
        return end("Application cancelled.")
    return con("Invalid choice.\n1. Confirm\n2. Cancel")


def _status(customer, rest):
    apps = list(customer.applications.order_by("-created_at")[:5])
    if not apps:
        return end("You have no loan applications yet.")
    lines = [f"{a.reference}: {_money(a.amount)} - {a.get_status_display()}" for a in apps]
    return end("Your applications:\n" + "\n".join(lines))


def _products_menu(rest):
    products = _active_products()
    if not products:
        return end("No loan products available right now.")

    if not rest:
        return con(f"Loan products (reply number):\n{_product_list(products)}")

    choice = rest[0]
    if not (choice.isdigit() and 1 <= int(choice) <= len(products)):
        return con(f"Invalid choice.\nLoan products (reply number):\n{_product_list(products)}")
    p = products[int(choice) - 1]
    return end(
        f"{p.name}\n{p.description}\nRate: {p.interest_rate}% p.a.\n"
        f"Max amount: {_money(p.max_amount)}\nMax period: {p.max_term_months} months"
    )


def _repayment(customer, rest):
    loans = list(
        customer.applications.filter(
            status__in=[LoanApplication.Status.APPROVED, LoanApplication.Status.DISBURSED]
        ).order_by("-created_at")[:5]
    )
    if not loans:
        return end("You have no active loans.")
    lines = []
    for a in loans:
        total, monthly = _schedule(a.product, a.amount, a.term_months)
        balance = total - a.amount_paid
        lines.append(f"{a.reference}: Bal {_money(balance)} of {_money(total)}")
    return end("Your loans:\n" + "\n".join(lines))


def ussd_menu(phone, text):
    # AT resends the full *-joined input history every request; the menu is replayed
    # from scratch rather than kept in a server-side session.
    customer = Customer.objects.filter(phone=phone).first()
    parts = text.strip().split("*") if text.strip() else []

    if customer is None:
        if not parts or not parts[0].strip():
            return con("Welcome to MkopoHub!\nPlease enter your full name:")
        customer, _ = Customer.objects.get_or_create(
            phone=phone, defaults={"name": parts[0].strip()}
        )
        nav = parts[1:]
    else:
        # A new user who registered earlier in this same session still carries their
        # typed name as parts[0]; strip it so navigation lines up for both cases.
        nav = parts[1:] if parts and parts[0] == customer.name else parts

    if not nav:
        return _main_menu(customer.name)

    section, rest = nav[0], nav[1:]
    handler = {"1": _apply, "2": _status, "3": _products_menu, "4": _repayment}.get(section)
    if handler is _products_menu:
        return handler(rest)
    if handler is None:
        return _main_menu(customer.name).replace("CON ", "CON Invalid choice.\n", 1)
    return handler(customer, rest)
