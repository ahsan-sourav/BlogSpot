"""
URL configuration for Main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from blogspot.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', home, name='home'),

    # User URLs
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('user_profile/', user_profile, name='user_profile'),
    path('blog_page/', blog_page, name='blog_page'),
    path('blog/<slug:slug>/', read_blog, name='read_blog'),
    path('blog/<int:blog_id>/like/', like_blog, name='like_blog'),
    path('blog/<int:blog_id>/comment/', comment_blog, name='comment_blog'),
    path('blog/<int:blog_id>/share/', share_blog, name='share_blog'),

    path('forum/', forum_home, name='forum_home'),
    path('forum/post/<int:post_id>/', forum_detail, name='forum_detail'),
    path('forum/new/', create_forum_post, name='create_forum_post'),
    path('forum/post/<int:post_id>/comment/', add_forum_comment, name='add_forum_comment'),

    # Blogger URLs
    path('blogger_register/', blogger_register, name='blogger_register'),
    path('blogger_login/', blogger_login, name='blogger_login'),
    path('blogger_logout/', blogger_logout, name='blogger_logout'),
    path('blogger_dashboard/', blogger_dashboard, name='blogger_dashboard'),
    path('blogger/manage/', manage_blogs, name='manage_blogs'),
    path('blogger/new/', create_or_update_blog, name='blog_create'),
    path('blogger/edit/<int:blog_id>/', create_or_update_blog, name='blog_update'),
    path('blogger/delete/<int:blog_id>/', delete_blog, name='blog_delete'),
    path('blogger/profile/', blogger_profile, name='blogger_profile'),

    # Message feature
    path('bloggers/', bloggers_list, name='bloggers_list'),
    path('send-message/<int:blogger_id>/', send_message, name='send_message'),
    path('user/inbox/', user_inbox, name='user_inbox'),
    path('blogger/inbox/', blogger_inbox, name='blogger_inbox'),
    path('blogger/reply/<int:message_id>/', reply_to_user, name='reply_to_user'),

    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),


    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()