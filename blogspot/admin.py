from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(BloggerProfile)
admin.site.register(Category)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Share)
admin.site.register(Message)
admin.site.register(ForumPost)
admin.site.register(ForumComment)


admin.site.site_header = "BlogSpot Admin"
admin.site.site_title = "BlogSpot Admin Portal"
admin.site.index_title = "Welcome to BlogSpot Admin"
