"""simulation URL 路由（F6-020~023）"""
from django.urls import path
from . import views

app_name = "simulation"

urlpatterns = [
    path("simulations/", views.trigger_simulation, name="trigger-simulation"),
    path("simulations/<str:batch_id>/", views.get_simulation, name="get-simulation"),
]
