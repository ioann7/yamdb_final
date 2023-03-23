from django.contrib import admin

from .models import Review, User


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    model = Review
    fields = ('title', 'text', 'author', 'score')
    search_fields = ('title', 'author', 'pub_date', 'score')
    list_filter = ('title', 'author', 'pub_date', 'score')
    empty_value_display = '-пусто-'


admin.site.register(User)
