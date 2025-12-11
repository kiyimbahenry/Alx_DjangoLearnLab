from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'total_likes', 'total_comments', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'total_likes', 'total_comments']
    fieldsets = [
        ('Basic Information', {
            'fields': ['author', 'title', 'content', 'image']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at', 'likes'],
            'classes': ['collapse']
        }),
    ]
    filter_horizontal = ['likes']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['truncated_content', 'author', 'post', 'total_likes', 'created_at', 'is_reply']
    list_filter = ['created_at', 'author', 'post']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at', 'total_likes']
    
    def truncated_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    truncated_content.short_description = 'Content'
