from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    phone_number = models.CharField(max_length=200, default="0", null=True)
    created_at = models.DateField(auto_now=True)
    modified_at = models.DateField(auto_now_add=True)
    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.SET_NULL,
    )

    @property
    def total_savings(self) -> float:
        return sum([budget.difference_in_income for budget in self.budget_set.all()])
    
    @property
    def total_budgeted_price(self) -> float:
        return sum([budget.projected_total_income for budget in self.budget_set.all()])

    def __str__(self) -> str:
        return self.user.first_name


class Budget(models.Model):
    NGN = "NGN"
    USD = "USB"
    GBP = "GBP"
    CURRENCIES = [
        (NGN, "Naira"),
        (USD, "US Dollars"),
        (GBP, "Pounds"),
    ]

    name = models.CharField(max_length=200, null=True)
    actual_total_income = models.FloatField(default=0.0)
    projected_total_income = models.FloatField(default=0.0)
    description = models.TextField(verbose_name="Budget description", null=True, blank=True)
    currency = models.CharField(
        max_length=3,
        choices=CURRENCIES,
        default=NGN,
    )
    created_at = models.DateField(auto_now=True)
    modified_at = models.DateField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    @property
    def difference_in_income(self) -> float:
        return self.actual_total_income - self.projected_total_income

    def __str__(self) -> str:
        return self.name


# the name 'Context' was chosen for lack of better word
class Context(models.Model):
    """
    The 'Context' is an entity within the Budget the contains several related items.

    e.g. A context can be 'House' which has sub items such as
    - Rent
    - Power bill
    - Water bill
    etc.
    """

    name = models.CharField(max_length=200, null=True)

    created_at = models.DateField(auto_now=True)
    modified_at = models.DateField(auto_now_add=True)

    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)

    # TODO 2: implement the method to get sub_total of projected amount for all items
    @property
    def items_total_projected_amount(self) -> float:
        return sum([item.projected for item in self.item_set.all()])

    # TODO 3: implement the method to get sub_total of actual amount for all items
    @property
    def items_total_actual_amount(self) -> float:
        return sum([item.actual for item in self.item_set.all()])

    # TODO 4: implement the method to get difference btwn sub_totals
    @property
    def difference_in_sub_totals(self) -> float:
        return self.items_total_actual_amount - self.items_total_projected_amount

    def __str__(self) -> str:
        return self.name


class Item(models.Model):
    """
    Item model is the actual item being budgetted for. It has the name of the item, projected and actual amounts.
    """

    name = models.CharField(max_length=200, null=True)
    projected = models.FloatField(default=0)
    actual = models.FloatField(default=0)

    created_at = models.DateField(auto_now=True)
    modified_at = models.DateField(auto_now_add=True)

    context = models.ForeignKey(Context, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name
