from rest_framework import serializers
from .models import Note , Collaborator

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id','title','description','color','image','is_archive','is_trash','reminder','user','label','collaborator']
        
        read_only_fields  = ("user","label","collaborator",)
        # fields = '__all__'


class CollaboratorSerializer(serializers.ModelSerializer):
     
    class Meta:
        model = Collaborator
        fields = '__all__'