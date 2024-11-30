from django.db import models

from django.contrib.auth import get_user_model

# Create your models here.

class Label(models.Model):
    name = models.CharField(max_length=255,null=False)
    color = models.CharField(max_length=50,null=True,blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    
    
    class Meta:
        db_table = 'label'
        
    def __str__(self):
        return self.name
    
    