from django.contrib import admin

from .models import Category, Location, Post, Comments


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'location',
        'is_published',
        'created_at',
        'pub_date',
    )
    list_editable = (
        'is_published',
        'pub_date',
    )
    search_fields = ('title',)
    list_filter = (
        'title',
        'author',
        'category',
        'location',
        'is_published',
        'created_at',
        'pub_date',
    )


class PostInline(admin.StackedInline):
    model = Post
    extra = 0
    ordering = ('-created_at', 'title')


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'created_at',
        'description',
    )
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_filter = (
        'title',
        'is_published',
        'created_at',
    )
    inlines = (PostInline,)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = (
        'name',
        'is_published',
        'created_at',
    )


admin.site.empty_value_display = 'Не задано'
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
# mfajf
