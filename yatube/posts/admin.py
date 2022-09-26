from django.contrib import admin

from posts.models import Follow, Post, Group, Comment


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
    )

    empty_value_display = '-пусто-'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
        'comments'
    )

    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )


@admin.register(Comment)
class CommentsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
    )
