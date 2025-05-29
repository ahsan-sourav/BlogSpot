from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.core.files.storage import default_storage


# User Registration
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = User.objects.create_user(username=username, password=password, email=email)
        UserProfile.objects.create(user=user)  
        messages.success(request, 'Account created successfully')
        return redirect('login')

    return render(request, 'auth/register.html')

# User Login
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Login successful')
            return redirect('home') 
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'auth/login.html')

# User Logout
@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')



@login_required
def user_profile(request):
    """Allow users to view and update their profile, and see shared blogs."""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile_picture')

        if bio:
            profile.bio = bio
        
        if profile_picture:
            # Delete old profile picture if exists
            if profile.profile_picture:
                default_storage.delete(profile.profile_picture.path)
            profile.profile_picture = profile_picture

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile')

    shared_blogs = Share.objects.filter(user=user).select_related('blog')

    return render(request, 'auth/user_profile.html', {
        'profile': profile,
        'shared_blogs': shared_blogs,
    })


# Blogger Registration
def blogger_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('blogger_register')

        user = User.objects.create_user(username=username, password=password, email=email)
        BloggerProfile.objects.create(user=user)  
        messages.success(request, 'Blogger account created successfully')
        return redirect('blogger_login')

    return render(request, 'auth/blogger_register.html')

# Blogger Login
def blogger_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'blogger_profile'):  
            auth_login(request, user)
            messages.success(request, 'Blogger login successful')
            return redirect('blogger_dashboard')  
        else:
            messages.error(request, 'Invalid credentials or not a blogger')
            return redirect('blogger_login')

    return render(request, 'auth/blogger_login.html')

# Blogger Logout
@login_required
def blogger_logout(request):
    auth_logout(request)
    messages.success(request, 'Blogger logged out successfully')
    return redirect('blogger_login')

# Blogger Dashboard
@login_required (login_url='blogger_login')
def blogger_dashboard(request):
    """Dashboard for bloggers to see stats on their blogs."""
    blogger_profile = get_object_or_404(BloggerProfile, user=request.user)  
    blogs = Blog.objects.filter(author=blogger_profile)

   
    total_blogs = blogs.count()
    total_views = sum(blog.total_views for blog in blogs)
    total_likes = sum(blog.likes.count() for blog in blogs)
    total_comments = sum(blog.comments.count() for blog in blogs)

    
    recent_comments = Comment.objects.filter(blog__author=blogger_profile).order_by('-created_at')[:5]

    context = {
        "total_blogs": total_blogs,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "recent_comments": recent_comments,
        "blogs": blogs,
    }
    return render(request, "blogger/dashboard.html", context)


@login_required (login_url='blogger_login')
def create_or_update_blog(request, blog_id=None):
    """ Handles both creating and updating a blog post. """
    blog = None
    if blog_id:
        blog = get_object_or_404(Blog, id=blog_id, author__user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        if not title or not content:
            messages.error(request, "Title and Content are required.")
            return redirect('blog_create' if not blog else 'blog_update', blog_id=blog_id)

        category = Category.objects.get(id=category_id) if category_id else None

        if blog:
            # Update existing blog
            blog.title = title
            blog.content = content
            blog.category = category
            if image:
                blog.image = image
            blog.save()
            messages.success(request, "Blog updated successfully.")
        else:
            # Create a new blog
            blogger_profile = get_object_or_404(BloggerProfile, user=request.user)
            blog = Blog.objects.create(
                title=title,
                slug=slugify(title),
                content=content,
                author=blogger_profile,
                category=category,
                image=image
            )
            messages.success(request, "Blog created successfully.")

        return redirect('manage_blogs')

    categories = Category.objects.all()
    return render(request, 'blog/blog_form.html', {'blog': blog, 'categories': categories})


@login_required (login_url='blogger_login')
def delete_blog(request, blog_id):
    """ Handles deleting a blog post. """
    blog = get_object_or_404(Blog, id=blog_id, author__user=request.user)
    if request.method == 'POST':
        blog.delete()
        messages.success(request, "Blog deleted successfully.")
        return redirect('blogger_dashboard')

    return render(request, 'blog/blog_confirm_delete.html', {'blog': blog})


@login_required (login_url='blogger_login')
def manage_blogs(request):
    """ View for bloggers to see, edit, and delete their blogs """
    if not hasattr(request.user, 'blogger_profile'):
        messages.error(request, "You are not a blogger.")
        return redirect('home')  

    blogs = request.user.blogger_profile.blogs.all() 
    return render(request, 'blog/manage_blogs.html', {'blogs': blogs})


# Home
def home(request):
    # blogs = Blog.objects.all()
    # categories = Category.objects.all()
    return render(request, 'home.html')

# Blog Page
def blog_page(request):
    """ View all blogs with optional filtering by category """
    category_id = request.GET.get('category')  
    if category_id:
        blogs = Blog.objects.filter(category_id=category_id)  
    else:
        blogs = Blog.objects.all()  

    categories = Category.objects.all()  
    return render(request, 'blog/blog_page.html', {'blogs': blogs, 'categories': categories})

# Read & View Blog 
def read_blog(request, slug):
    """ View a blog post and count total views """
    blog = get_object_or_404(Blog, slug=slug)

    # Increase view count only if it's a new visit
    session_key = f"viewed_blog_{blog.id}"
    if not request.session.get(session_key, False):
        blog.total_views += 1
        blog.save(update_fields=['total_views'])
        request.session[session_key] = True

    comments = blog.comments.all()
    total_likes = blog.likes.count()
    total_shares = blog.shares.count()

    return render(request, 'blog/read_blog.html', {
        'blog': blog,
        'comments': comments,
        'total_likes': total_likes,
        'total_shares': total_shares,
    })

# Like a Blog
@login_required (login_url='login')
def like_blog(request, blog_id):
    """ Allow logged-in users to like a blog """
    blog = get_object_or_404(Blog, id=blog_id)
    like, created = Like.objects.get_or_create(blog=blog, user=request.user)

    if not created:
        like.delete()
        messages.info(request, "You unliked this blog.")
    else:
        messages.success(request, "You liked this blog!")

    return redirect('read_blog', slug=blog.slug)

# Comment on a Blog
@login_required (login_url='login')
def comment_blog(request, blog_id):
    """ Allow users to comment on a blog """
    if request.method == "POST":
        blog = get_object_or_404(Blog, id=blog_id)
        content = request.POST.get("content")

        if content.strip():
            Comment.objects.create(blog=blog, user=request.user, content=content)
            messages.success(request, "Comment added successfully.")
        else:
            messages.error(request, "Comment cannot be empty.")

    return redirect('read_blog', slug=blog.slug)

# Share a Blog
@login_required (login_url='login')
def share_blog(request, blog_id):
    """ Allow users to share a blog """
    blog = get_object_or_404(Blog, id=blog_id)
    Share.objects.create(blog=blog, user=request.user)
    messages.success(request, "You shared this blog!")

    return redirect('read_blog', slug=blog.slug)


# List all forum posts
def forum_home(request):
    posts = ForumPost.objects.all().order_by('-created_at')
    return render(request, 'forum/forum_home.html', {'posts': posts})


def forum_detail(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    comments = post.comments.all().order_by('-created_at')  
    return render(request, 'forum/forum_detail.html', {'post': post, 'comments': comments})

# Create a new forum post
@login_required(login_url='login')
def create_forum_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        if not title or not content:
            messages.error(request, "Title and content are required.")
            return redirect('create_forum_post')

        ForumPost.objects.create(title=title, content=content, author=request.user)
        messages.success(request, "Forum post created successfully!")
        return redirect('forum_home')

    return render(request, 'forum/forum_create.html')

# Add a comment to a forum post
@login_required(login_url='login')
def add_forum_comment(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ForumComment.objects.create(forum=post, user=request.user, content=content)
            messages.success(request, "Comment added!")
        else:
            messages.error(request, "Comment cannot be empty.")
    return redirect('forum_detail', post_id=post.id)



# Blogger Profile
@login_required(login_url='blogger_login')
def blogger_profile(request):
    blogger_profile = get_object_or_404(BloggerProfile, user=request.user)

    if request.method == 'POST':
        bio = request.POST.get('bio')
        profession = request.POST.get('profession')
        website = request.POST.get('website')
        profile_picture = request.FILES.get('profile_picture')

        blogger_profile.bio = bio
        blogger_profile.profession = profession
        blogger_profile.website = website

        if profile_picture:
            blogger_profile.profile_picture = profile_picture

        blogger_profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('blogger_profile')

    return render(request, 'auth/profile.html', {'profile': blogger_profile})



@login_required(login_url='login')
def bloggers_list(request):
    bloggers = BloggerProfile.objects.all()
    return render(request, 'message/bloggers_list.html', {'bloggers': bloggers})

# Send message 
@login_required(login_url='login')
def send_message(request, blogger_id):
    blogger = get_object_or_404(BloggerProfile, id=blogger_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            
            Message.objects.create(sender=request.user, receiver=blogger.user, content=content)
            messages.success(request, "Message sent successfully!")
        else:
            messages.error(request, "Message cannot be empty.")

    return redirect('bloggers_list')



# User inbox
@login_required(login_url='login')
def user_inbox(request):
    messages_received = Message.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'message/user_inbox.html', {'messages_received': messages_received})

# Blogger inbox 
@login_required(login_url='blogger_login')
def blogger_inbox(request):
    messages_received = request.user.received_messages.all().order_by('-created_at')
    unread_count = messages_received.filter(is_read=False).count()

    return render(request, 'message/blogger_inbox.html', {
        'messages_received': messages_received,
        'unread_count': unread_count,
    })



# Blogger replies 
@login_required(login_url='blogger_login')
def reply_to_user(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)

    if request.method == 'POST':
        content = request.POST.get('reply')
        if content:
            
            Message.objects.create(sender=request.user, receiver=message.sender, content=content)
            message.is_read = True
            message.save()
            messages.success(request, "Reply sent!")
        else:
            messages.error(request, "Reply cannot be empty.")

    return redirect('blogger_inbox')


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')