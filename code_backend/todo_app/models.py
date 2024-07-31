from django.db import models

# Create your models here.


class Todo(models.Model):
    title = models.CharField(max_length=212)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)
