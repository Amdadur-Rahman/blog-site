from django.shortcuts import render, get_object_or_404
from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank
)
# Create your views here.

def post_list(request,tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(
            Tag,
            slug=tag_slug
        )
        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, 2)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render (request,'blog/post_list.html',{
        'posts':posts,
        'tag':tag
        })

def post_detail(request, day, month, year, post):
    post = get_object_or_404(
        Post,
        slug=post,
        publish__day=day,
        publish__month=month,
        publish__year=year,
        status = Post.Status.PUBLISH
    )
    comments = post.comments.filter(active=True)
    form = CommentForm()

    post_tags_ids = post.tags.values_list('id',flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags','-publish')

    return render (request,'blog/post_detail.html',{
        'post':post,
        'comments':comments,
        'form':form,
        'similar_posts':similar_posts
        })


def post_share(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISH
    )
    sent=False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} ({cd['email']}) plese read this post{post.title}"
            message = f"plese click this link and red this post {post.title} {post_url}\n\n {cd['comments']}"
            send_mail(
                subject,
                message,
                None,
                [cd['to']]
            )
            sent=True
    else:
        form = EmailPostForm()
    return render (request,'blog/post_share.html',{
        'post':post,
        'form':form,
        'sent':sent
    })

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISH
    )
    comment = None
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render (request,'blog/post_comment.html',{
        'post':post,
        'form':form,
        'comment':comment
    })

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = (
                Post.published.annotate(
                    similarity=TrigramSimilarity('body', query) 
                ).filter(
                    similarity__gt=0.1
                    ).order_by('-similarity')
            )
    return render (request,'blog/post_search.html',{
        'form':form,
        'query':query,
        'results':results
    })
    