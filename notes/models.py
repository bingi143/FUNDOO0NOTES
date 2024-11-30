from django.db import models
from django.contrib.auth import get_user_model
from user.models import User
from label.models import Label

# Create your models here.
    
class Note(models.Model):
    title = models.CharField(max_length=200,null=False,db_index=True)
    description = models.TextField(null=True,blank=True)
    color = models.CharField(max_length=50,null=True,blank=True)
    image = models.ImageField(null=True,blank=True)
    is_archive = models.BooleanField(default=False,db_index=True)
    is_trash = models.BooleanField(default=False,db_index=True)
    reminder = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    collaborator = models.ManyToManyField(User, related_name="collaborator_note_set", through='Collaborator')
    label = models.ManyToManyField(Label,related_name='label')
      
    
    def __str__(self):
        return self.title
    
    
class Collaborator(models.Model):
    read_only= 'read_only'
    read_write = 'read_write'

    access_type_choices = [
        (read_only, 'Read Only'),
        (read_write, 'Read and Write'),
    ]

    note_id = models.ForeignKey(Note,on_delete=models.CASCADE,related_name='collaborators_set')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    access_type = models.CharField(max_length=20, choices=access_type_choices, default=read_only)

    class Meta:
        unique_together = ('user_id', 'note_id')
        
        
    # def __str__(self):
    #     return f"{self.user.username} - {self.note.title} ({self.access_type})"
    