from django.contrib import admin

from .models import Profile, Budget, Context, Item


admin.site.register(Profile)
admin.site.register(Budget)
admin.site.register(Context)
admin.site.register(Item)
