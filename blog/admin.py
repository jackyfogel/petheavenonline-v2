from django.contrib import admin
from .models import Category, BlogPost, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'published_at']
    list_filter = ['status', 'category', 'published_at']
    search_fields = ['title', 'content', 'seo_title', 'seo_description']
    prepopulated_fields = {'slug': ('title',)}  # auto-fill slug from title
    date_hierarchy = 'published_at'
    ordering = ['-published_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_on']
    search_fields = ['author', 'body']
    list_filter = ['created_on']
