from django.contrib import admin

from .models import Category, Location, Post, Comments


class PaginatorMixin:
    list_per_page = 10
    list_max_show_all = 1000


class PostAdmin(PaginatorMixin, admin.ModelAdmin):
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


class CategoryAdmin(PaginatorMixin, admin.ModelAdmin):
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


class LocationAdmin(PaginatorMixin, admin.ModelAdmin):
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


class CommentsAdmin(PaginatorMixin, admin.ModelAdmin):
    list_display = (
        'post',
        'created_at',
        'author',
        'short_comment',
    )
    search_fields = (
        'post__title', 'author__username', 'text',
    )
    list_filter = (
        'post',
        'author',
        'created_at',
    )

    def short_comment(self, obj):
        max_len = 50
        return (f'{obj.text[:max_len]}...'
                if len(obj.text) > max_len else
                obj.text)

    short_comment.short_description = 'Коментарий'


admin.site.empty_value_display = 'Не задано'
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Comments, CommentsAdmin)
