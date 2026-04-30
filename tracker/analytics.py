from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Transaction


def total_spend(user):
    return (
        Transaction.objects
        .filter(user=user)
        .aggregate(total=Sum("amount"))["total"] or 0
    )


def category_spend(user):
    return (
        Transaction.objects
        .filter(user=user)
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )


def top_merchants(user):
    return (
        Transaction.objects
        .filter(user=user)
        .values("merchant")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:5]
    )


def monthly_trend(user):
    return (
        Transaction.objects
        .filter(user=user)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

