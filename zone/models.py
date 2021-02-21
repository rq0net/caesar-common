from django.db import models

# Create your models here.
class Czone(models.Model):
    domain = models.CharField(max_length=30)
    realm = models.CharField(max_length=30)
    user_domain = models.CharField(max_length=30)
    cluster = models.CharField(max_length=30)
    
    def __str__(self):
        return self.domain