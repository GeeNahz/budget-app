from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.indexView, name="index"),
    path("budget/", views.budgetsView, name="budgets"),
    path("budget/<int:pk>/", views.budgetView, name="budget"),
    path(
        "budget/create/",
        views.createBudgetView,
        name="create_budget",
    ),
    path(
        "budget/<int:pk>/edit/",
        views.editBudget,
        name="edit-budget",
    ),
    path(
        "budget/context/create/",
        views.createContextView,
        name="create-context",
    ),
    path(
        "budget/context/<int:pk>/edit/",
        views.editContextView,
        name="edit-context",
    ),
    path(
        "budget/item/create/",
        views.createItemView,
        name="create-item",
    ),
    path(
        "budget/item/<int:pk>/edit/",
        views.editItemView,
        name="edit-item",
    ),
    path("signup/", views.signupView, name="signup"),
    path("signin/", views.signinView, name="signin"),
    path("signout/", views.signoutView, name="signout"),
]
