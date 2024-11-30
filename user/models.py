from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager
# Create your models here.

class User(AbstractUser):
    username =  None
    email = models.EmailField(_("email address"), unique=True)
    is_verified=models.BooleanField(default=False)
    
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    class Meta:
        db_table = "user"
        
        
    def __str__(self):
        return self.email
    
    
class Log(models.Model):
    method = models.CharField(max_length=10,null=False)
    url = models.TextField(null=False)
    count = models.IntegerField(default=1)
    
    class Meta:
        db_table = "log"
        
    def __str__(self):
        return self.method
    
    
    
    

