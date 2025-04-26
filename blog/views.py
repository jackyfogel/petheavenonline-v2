from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import BlogPost
# Create your views here.

def blog_home(request):
    return render(request,'blog/index.html')

def blog_list(request):
    posts = BlogPost.objects.filter(status='published').order_by('-published_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})

def blog_post(request, year, month, slug):
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        published_at__year=year,
        published_at__month=month
    )
    return render(request, 'blog/blog_post.html', {'post': post})
