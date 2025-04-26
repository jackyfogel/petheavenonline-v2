from django.db import models
from django.utils.text import slugify
from django.urls import reverse




# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    COMMENT_STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    featured_image = models.ImageField(upload_to='blog/featured_images', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.TextField(max_length=170, blank=True)
    seo_canonical = models.URLField(max_length=300, blank=True, null=True)



    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_post', args=[
            self.published_at.year,
            self.published_at.month,
            self.slug,

        ])
    def __str__(self):
        return self.title
class Comment(models.Model):
    author = models.CharField(max_length=100)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey('BlogPost', on_delete=models.CASCADE)








