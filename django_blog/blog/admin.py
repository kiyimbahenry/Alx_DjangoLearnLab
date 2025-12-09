from django.contrib import admin
from .models import Post, Comment
from taggit.models import Tag
from taggit.admin import TagAdmin as TaggitTagAdmin


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_posted', 'get_tags_list')
    list_filter = ('date_posted', 'author', 'tags')
    search_fields = ('title', 'content')
    filter_horizontal = ()  # Remove 'tags' from here or leave empty
    
    def get_tags_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    get_tags_list.short_description = 'Tags'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at', 'short_content')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username', 'post__title')
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'


# Register/Unregister Tag model properly
admin.site.unregister(Tag)  # Unregister default
admin.site.register(Tag, TaggitTagAdmin)  # Register with taggit's admin
