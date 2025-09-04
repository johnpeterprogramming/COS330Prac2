from django.contrib import admin

# Register your models here.
from .models import EncryptedImage, EncryptedDocument

admin.site.register(EncryptedImage)
admin.site.register(EncryptedDocument)