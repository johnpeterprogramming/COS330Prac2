from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import EncryptedImage
from .utils.encryption import save_encrypted_image, get_decrypted_image
from .forms import RegisterForm, LoginForm, UploadImageForm

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None and user.is_active:
                login(request, user)
                return redirect("dashboard")
            form.add_error(None, "Inactive account.")
    else:
        form = LoginForm(request)
    return render(request, "login.html", {"form": form})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user: User = form.save(commit=False)
            user.email = form.cleaned_data["email"].lower()
            user.is_active = False  # Require admin approval
            user.save()
            return render(request, "register.html", {"form": RegisterForm(), "success": "Registration successful. Await admin approval."})
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

def dashboard(request):
    return render(request, "dashboard.html")

# Helper function to check roles
def group_required(*group_names):
    def in_groups(user):
        if user.is_authenticated:
            if user.is_superuser or bool(user.groups.filter(name__in=group_names)):
                return True
        return False
    return user_passes_test(in_groups)

# @login_required
# @group_required('Admin', 'Manager')
# def upload_image(request):
#     if request.method == "POST":
#         uploaded_file = request.FILES['image']
#         title = request.POST['title']
#         save_encrypted_image(uploaded_file, title)
#         return HttpResponse("Image uploaded.")
#     return render(request, "upload.html")

@login_required
def view_image(request, image_id):
    image: EncryptedImage = get_object_or_404(EncryptedImage, id=image_id)
    img_bytes = get_decrypted_image(image)

    return HttpResponse(img_bytes, content_type="image/jpeg")

@login_required
def view_documents(request):
    return render(request, "documents.html")

@login_required
def view_confidential(request):
    return render(request, "confidential.html")

def images(request):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            uploaded_file = form.cleaned_data['image']
            save_encrypted_image(uploaded_file, title)
            return redirect('images')
    else:
        form = UploadImageForm()
    images = EncryptedImage.objects.all().order_by('-id')
    return render(request, "images.html", {"images": images, "form": form})