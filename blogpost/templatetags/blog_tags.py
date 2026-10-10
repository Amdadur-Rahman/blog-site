from django import template
from ..models import Post
from django.db.models import Count


register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()

@register.inclusion_tag('blog/last_posts.html')
def show_last_posts(count=5):
    last_posts = Post.published.order_by('-publish')[:count]
    return {'last_posts':last_posts}

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments', '-publish')[:count]