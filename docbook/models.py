from django.db import models


# Create your models here.

class XMLDoc(models.Model):
    id = models.CharField(max_length=512, primary_key = True)
    name = models.CharField(max_length=256)
    content = models.TextField()
