from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 2)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render (request,'blog/post_list.html',{'posts':posts})

def post_detail(request, day, month, year, post):
    post = get_object_or_404(
        Post,
        slug=post,
        publish__day=day,
        publish__month=month,
        publish__year=year,
        status = Post.Status.PUBLISH
    )
    return render (request,'blog/post_detail.html',{'post':post})
