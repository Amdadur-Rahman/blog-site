from django.contrib import admin
from .models import Post


# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title','slug','author','created','updated','publish','status']
    list_filter = ['author','status','created','updated','publish']
    search_fields = ['title','body']
    prepopulated_fields = {'slug' : ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status','publish']
    show_facets = admin.ShowFacets.ALWAYS
