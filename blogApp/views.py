from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "index.html", {
        'posts': Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already Exists")
                return redirect('signup')
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already Exists")
                return redirect('signup')
            else:
                User.objects.create_user(username=username, email=email, password=password).save()
                return redirect('signin')
        else:
            messages.info(request, "Password should match")
            return redirect('signup')

    return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("index")
        else:
            messages.info(request, 'Username or Password is incorrect')
            return redirect("signin")

    return render(request, "signin.html")
