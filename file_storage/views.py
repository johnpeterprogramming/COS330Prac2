from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
import os
from .models import EncryptedImage
from .utils.encryption import save_encrypted_image, get_decrypted_image, encrypt_bytes
from .forms import RegisterForm, LoginForm, UploadImageForm, UpdateImageForm

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
@group_required('Admin', 'Manager')
def delete_image(request, image_id):
    if request.method == 'POST':
        image: EncryptedImage = get_object_or_404(EncryptedImage, id=image_id)
        
        # Delete the physical file
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
        
        image.delete()
        
        messages.success(request, "Image successfully deleted")
        return redirect("images")
    
    # If GET request, show confirmation page
    image = get_object_or_404(EncryptedImage, id=image_id)
    return render(request, "confirm_delete.html", {"image": image})


@login_required
@group_required('Admin', 'Manager')
def update_image(request, image_id):
    image = get_object_or_404(EncryptedImage, id=image_id)
    
    if request.method == 'POST':
        form = UpdateImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Update title
            image.title = form.cleaned_data['title']
            
            # If new image uploaded, replace the encrypted file
            if form.cleaned_data['image']:
                # Delete old file
                if os.path.exists(image.file_path):
                    os.remove(image.file_path)
                
                # Save new encrypted image
                uploaded_file = form.cleaned_data['image']
                img_bytes = uploaded_file.read()
                encrypted = encrypt_bytes(img_bytes)
                
                # Save to same path or generate new one
                folder = os.path.join(settings.MEDIA_ROOT, "images")
                os.makedirs(folder, exist_ok=True)
                filename = f"{image.title}.bin"
                file_path = os.path.join(folder, filename)
                
                with open(file_path, "wb") as f:
                    f.write(encrypted)
                
                image.file_path = file_path
            
            image.save()
            messages.success(request, "Image successfully updated")
            return redirect("images")
    else:
        # Pre-populate form with current data
        form = UpdateImageForm(initial={'title': image.title})
    
    return render(request, "update_image.html", {"form": form, "image": image})

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