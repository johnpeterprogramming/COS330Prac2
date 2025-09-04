from django.db import models


class EncryptedImage(models.Model):
    title = models.CharField(max_length=128)
    file_path = models.CharField(max_length=256)

    def __str__(self):
        return "Image " + self.title

class EncryptedDocument(models.Model):
    title = models.CharField(max_length=128)
    file_path = models.CharField(max_length=256)

    def __str__(self):
        return "Document " + self.title