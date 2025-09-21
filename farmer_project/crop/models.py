from django.db import models
from farmer.models import Farmer

class Crop(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    planting_date = models.DateField()
    harvest_date = models.DateField()
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class LearningContent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='learning_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title