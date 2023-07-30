from enum import Enum

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.shortcuts import render

from accounts.utils.reverse_querystring import reverse_querystring

from .forms import (
    SigninForm,
    SignupForm,
    CreateBudgetForm,
    CreateContextForm,
    CreateItemForm,
)

from .models import Profile, Budget, Context, Item


class SubmitType(Enum):
    _save = "_save"
    _continue = "_continue"
    _addanother = "_addanother"
    _next = "_next"


def signupView(request):
    """
    Register and create account for a client
    """

    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()

            Profile.objects.create(
                user=user,
            )

            username = form.cleaned_data["username"]
            messages.success(
                request=request,
                message=f"Account successfully create for { username }",
            )

            return HttpResponseRedirect(reverse("accounts:signin"))
        else:
            messages.error(
                request=request,
                message="The details provided were in-correct.",
            )

    form = SignupForm()
    context = {"form": form}

    return render(request, "accounts/pages/signup.html", context)


def signinView(request):
    """
    Log in a user to session
    """

    from django.conf import settings

    print("SETTINGS: ", settings.LOGIN_URL)
    print("REQUEST PATH: ", request.path)

    print("USER: ", request.user)

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request=request, user=user)

            return HttpResponseRedirect(reverse("accounts:index"))
        else:
            messages.error(request, message="Username or password is incorrect")
            form = SigninForm()
            context = {"form": form}

            return render(request, "accounts/pages/signin.html", context)

    form = SigninForm()
    context = {"form": form}

    return render(request, "accounts/pages/signin.html", context)


def signoutView(request):
    """
    Log user out of session
    """
    logout(request=request)

    return HttpResponseRedirect(reverse("accounts:signin"))


@login_required
def indexView(request):
    budgets = request.user.profile.budget_set.all()
    ctx = Context.objects.filter(budget__profile_id=request.user.profile.id)
    recent_items = Item.objects.filter(
        context__budget__profile_id=request.user.profile.id
    ).order_by("-created_at")[:5]

    total_budgets = budgets.count()
    total_contexts = ctx.count()
    context = {
        "budgets": budgets,
        "total_budgets": total_budgets,
        "total_contexts": total_contexts,
        "recent_items": recent_items,
    }

    return render(request, "accounts/pages/index.html", context)


@login_required
def budgetView(request, pk):
    budget = request.user.profile.budget_set.get(pk=pk)
    contexts = request.user.profile.budget_set.get(pk=pk).context_set.all()

    items = Item.objects.filter(context__budget__profile_id=request.user.profile.id)

    data = {
        "budget": budget,
        "contexts": contexts,
        "items": items,
    }

    return render(request, "accounts/pages/d_budget.html", data)


@login_required
def budgetsView(request):
    budgets = request.user.profile.budget_set.all()

    data = {"budgets": budgets}

    return render(request, "accounts/pages/d_budgets.html", data)


@login_required
def editBudget(request, pk):
    profile = request.user.profile
    if request.method == "POST":
        old_data = request.user.profile.budget_set.get(pk=pk)
        form = CreateBudgetForm(request.POST, instance=old_data)

        if form.is_valid():
            # handle the various submit cases
            form.save()

            submit_type = str(list(request.POST.dict())[-1])

            match submit_type:
                case str(SubmitType._save.name):
                    return HttpResponseRedirect(
                        reverse(
                            "accounts:budget",
                            args=[pk],
                        )
                    )
                case str(SubmitType._addanother.name):
                    return render(
                        request,
                        "accounts/pages/create_edit_budget.html",
                        {"form": CreateBudgetForm()},
                    )
                case str(SubmitType._next.name):
                    return HttpResponseRedirect(
                        reverse_querystring(
                            view="accounts:create-context",
                            query_kwargs={
                                "budget_id": old_data.id,
                            },
                        )
                    )
                case _:
                    print("Invalid input type")
        else:
            messages.error(request, "Details submitted were in-correct.")

    budget = request.user.profile.budget_set.get(pk=pk)

    form = CreateBudgetForm(initial={"profile": profile}, instance=budget)
    data = {"form": form}

    return render(
        request,
        "accounts/pages/create_edit_budget.html",
        data,
    )


@login_required
def createBudgetView(request):
    if request.method == "POST":
        form = CreateBudgetForm(request.POST)

        if form.is_valid():
            submit_type = str(list(request.POST.dict())[-1])

            name = form.cleaned_data["name"]
            actual_total_income = form.cleaned_data["actual_total_income"]
            projected_total_income = form.cleaned_data["projected_total_income"]
            currency = form.cleaned_data["currency"]

            budget = Budget(
                profile=request.user.profile,
                name=name,
                actual_total_income=actual_total_income,
                projected_total_income=projected_total_income,
                currency=currency,
            )
            budget.save()

            match submit_type:
                case str(SubmitType._save.name):
                    return HttpResponseRedirect(reverse("accounts:budgets"))
                case str(SubmitType._addanother.name):
                    return render(
                        request,
                        "accounts/pages/create_edit_budget.html",
                        {"form": CreateBudgetForm()},
                    )
                case str(SubmitType._next.name):
                    return HttpResponseRedirect(
                        reverse_querystring(
                            view="accounts:create-context",
                            query_kwargs={
                                "budget_id": budget.id,
                            },
                        )
                    )
                case _:
                    print("Invalid input type")

        else:
            messages.error(request, "Details submitted were in-correct.")

    profile = request.user.profile

    form = CreateBudgetForm(initial={"profile": profile})

    context = {
        "form": form,
    }

    return render(
        request,
        "accounts/pages/create_edit_budget.html",
        context,
    )


@login_required
def editContextView(request, pk):
    context = Context.objects.get(pk=pk)

    if request.method == "POST":
        form = CreateContextForm(request.POST, instance=context)

        if form.is_valid():
            new_context = form.save()

            budget_id = request.POST["budget"]

            submit_type = str(list(request.POST.dict())[-1])

            match submit_type:
                case str(SubmitType._save.name):
                    return HttpResponseRedirect(
                        reverse_querystring(
                            view="accounts:budget",
                            query_kwargs={
                                "budget_id": budget_id,
                            },
                        )
                    )
                case str(SubmitType._next.name):
                    return HttpResponseRedirect(
                        reverse_querystring(
                            view="accounts:create-item",
                            query_kwargs={
                                "context_id": new_context.id,
                            },
                        )
                    )
                case str(SubmitType._addanother.name):
                    return HttpResponseRedirect(
                        reverse_querystring(
                            view="accounts:create-context",
                            query_kwargs={
                                "budget_id": budget_id,
                            },
                        )
                    )
                case _:
                    print("Invalid submit option")

    form = CreateContextForm(instance=context)

    data = {"form": form}

    return render(
        request,
        "accounts/pages/create_edit_context.html",
        data,
    )


@login_required
def createContextView(request):
    form = None
    budget_id = request.GET.get("budget_id")

    if request.method == "POST":
        print("POST DATA: ", request.POST)
        print("GET DATA: ", request.GET)
        form = CreateContextForm(request.POST)
        if form.is_valid():
            new_context = form.save()

            submit_type = str(list(request.POST.dict())[-1])

            match submit_type:
                case str(SubmitType._save.name):
                    # instead route to that specific budget page
                    return HttpResponseRedirect(reverse("accounts:budgets"))
                case str(SubmitType._next.name):
                    return HttpResponseRedirect(
                        reverse_querystring(
                            view="accounts:create-item",
                            query_kwargs={
                                "context_id": new_context.id,
                            },
                        )
                    )
                case str(SubmitType._addanother.name):
                    return HttpResponseRedirect(
                        reverse_querystring(
                            view="accounts:create-context",
                            query_kwargs={
                                "budget_id": budget_id,
                            },
                        )
                    )
                case _:
                    print("Invalid submit option")

    form = CreateContextForm()

    if budget_id is not None:
        budget = Budget.objects.get(pk=int(budget_id))
        form.initial = {"budget": budget}

    context = {"form": form}

    return render(
        request,
        "accounts/pages/create_edit_context.html",
        context,
    )


@login_required
def createItemView(request):
    context_id = request.GET.get("context_id")

    if request.method == "POST":
        formdata = CreateItemForm(request.POST)

        if formdata.is_valid():
            new_item = formdata.save()

            budget_id = Item.objects.get(pk=new_item.id).context.budget.id

            submit_type = str(list(request.POST.dict())[-1])

            match submit_type:
                case str(SubmitType._save.name):
                    return HttpResponseRedirect(
                        reverse_querystring(
                            view="accounts:budget",
                            kwargs={"pk": budget_id},
                        )
                    )
                case str(SubmitType._next.name):
                    return HttpResponseRedirect(
                        reverse_querystring(
                            view="accounts:create-context",
                            query_kwargs={
                                "budget_id": budget_id,
                            },
                        )
                    )
                case str(SubmitType._addanother.name):
                    return (
                        HttpResponseRedirect(
                            reverse_querystring(
                                view="accounts:create-item",
                                query_kwargs={
                                    "context_id": context_id,
                                },
                            )
                        )
                        if context_id is not None
                        else HttpResponseRedirect(
                            reverse_querystring(
                                view="accounts:create-item",
                            )
                        )
                    )
                case _:
                    print("Invalid submit option")

    form = CreateItemForm()

    if context_id is not None:
        context = Context.objects.get(pk=context_id)
        form.initial = {"context": context}

    data = {"form": form}

    return render(
        request,
        "accounts/pages/create_edit_item.html",
        data,
    )
