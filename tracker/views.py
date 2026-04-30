import csv
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Transaction, Category
from .rules import categorize_merchant
from .analytics import total_spend, category_spend, top_merchants, monthly_trend

from django.contrib.auth.decorators import login_required
# -----------------------------
# CSV INGESTION (ETL LAYER)
# -----------------------------
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import csv

from .models import Transaction, Category
from .rules import categorize_merchant


@login_required
@csrf_exempt
def upload_csv(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    if "file" not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    file = request.FILES["file"]

    decoded = file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(decoded)

    inserted = 0
    errors = []

    for i, row in enumerate(reader):
        try:
            category_name = categorize_merchant(row["merchant"])
            category = Category.objects.get_or_create(name=category_name)[0]

            # ✅ FIXED DATE HANDLING (robust)
            date_str = row["date"]
            date = None

            for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                try:
                    date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue

            if not date:
                errors.append(f"Row {i+1}: Invalid date format {date_str}")
                continue

            Transaction.objects.create(
                user=request.user,
                amount=float(row["amount"]),
                merchant=row["merchant"],
                description=row.get("description", ""),
                date=date,
                category=category
            )

            inserted += 1

        except Exception as e:
            errors.append(f"Row {i+1}: {str(e)}")

    return JsonResponse({
        "message": "CSV processed successfully",
        "rows_inserted": inserted,
        "errors": errors
    })

# -----------------------------
# ANALYTICS API (JSON VERSION)
# -----------------------------
def dashboard_api(request):
    user = request.user

    data = {
        "total_spend": total_spend(user),
        "category_spend": list(category_spend(user)),
        "monthly_trend": list(monthly_trend(user)),
    }

    return JsonResponse(data)


# -----------------------------
# DASHBOARD UI (HTML VERSION)
# -----------------------------
import json

from .ai_engine import generate_ai_insight

import json

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    user = request.user

    category_data = list(category_spend(user))
    trend_data = list(monthly_trend(user))

    # 🔥 FIX Decimal + date issues
    for item in category_data:
        item["total"] = float(item["total"] or 0)

    for item in trend_data:
        item["total"] = float(item["total"] or 0)
        item["month"] = item["month"].strftime("%Y-%m")  # fix date

    total = float(total_spend(user) or 0)

    data = {
        "total_spend": total,
        "category_spend": category_data,
        "monthly_trend": trend_data,
    }

    ai_insight = generate_ai_insight(data)

    context = {
        "total_spend": total,
        "category_json": json.dumps(category_data),
        "trend_json": json.dumps(trend_data),
        "ai_insight": ai_insight,
    }

    return render(request, "tracker/dashboard.html", context)

from .ai_engine import generate_ai_insight

def ai_insights(request):
    data = {
        "total_spend": total_spend(),
        "category_spend": list(category_spend()),
        "monthly_trend": list(monthly_trend()),
    }

    insight = generate_ai_insight(data)

    return JsonResponse({
        "insight": insight,
        "raw_data": data
    })

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()   # create user
            login(request, user) # 🔥 auto login
            return redirect('dashboard')  # go to dashboard
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})

from django.shortcuts import render, redirect
from .forms import TransactionForm
from django.contrib.auth.decorators import login_required

@login_required
def add_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            txn = form.save(commit=False)
            txn.user = request.user  # 🔥 IMPORTANT
            txn.save()
            return redirect('/dashboard/')
    else:
        form = TransactionForm()

    return render(request, "tracker/add_transaction.html", {"form": form})


def home(request):
    return render(request, "tracker/home.html")