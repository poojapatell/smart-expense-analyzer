from django.urls import path
from .views import upload_csv, dashboard, ai_insights, signup, add_transaction, home

urlpatterns = [
    path("upload/", upload_csv),
    path("", home, name="home"),   # 🔥 HOME PAGE
    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/", dashboard, name='dashboard'),
    path("ai-insights/", ai_insights),
    path('signup/', signup, name='signup'),
    path('add/', add_transaction, name='add_transaction'),
]