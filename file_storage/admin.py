from django.contrib import admin

# Register your models here.
from .models import EncryptedImage

admin.site.register(EncryptedImage)