from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from .models import Note ,Collaborator
from user.models import User
from .serializers import NoteSerializer , CollaboratorSerializer
from loguru import logger
from .redisutil import RedisUtils
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from datetime import datetime
from user.task import send_reminder
from django.shortcuts import get_object_or_404
import json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from label.models import Label

class NoteViewSet(viewsets.ModelViewSet):
    
    """
    A viewset for viewing and editing note instances.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    redis = RedisUtils()
    
    """ Swagger_atuo_schema()"""
    @swagger_auto_schema( operation_description="An Notes curd operatuon API endpoint",
        request_body=NoteSerializer,
        responses={200: NoteSerializer(many=True)})
    
 
    def get_queryset(self):
        """
        Returns notes for the logged-in user with is_archive and is_trash as False.
        """
        lookup=Q(user=self.request.user)|Q(collaborator__id=self.request.user.id)
        return Note.objects.filter(lookup,is_archive=False, is_trash=False).distinct('id')
        
        # return Note.objects.filter(user=self.request.user, is_archive=False, is_trash=False)

    def list(self, request, *args, **kwargs):
        """
        List all notes for the logged-in user that are not archived or trashed.
        """
        try:
            cache_key = f"user_{request.user.id}"
            cache_note = self.redis.get(cache_key)
            print(cache_note)

            if cache_note:
                logger.info(f"Notes feteched from the cache for user {request.user.id}")
                return Response({"Message":"The list of cache notes of user","satus":"Sucess","data":cache_note},status=status.HTTP_200_OK)
                
            queryset = self.get_queryset()
            # print(f"querset = {queryset}")
            serializer = self.get_serializer(queryset, many=True)
            # print(f"ser = {serializer}")
            
            
            self.redis.save(cache_key,serializer.data,ex=300)
            return Response({"Message":"The list of notes of user ","status":"Sucess","data":serializer.data},status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving notes: {str(e)}")
            return Response({
                'error': 'An error occurred while retrieving notes.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
    def sechdule_reminder(self,note,reminder_time):
        try:
           
            reminder_time=datetime.strptime(reminder_time, "%Y-%m-%dT%H:%M")
            # print(reminder_time)
            task_name = f'reminder-task-{note.id}'
            periodic_task= PeriodicTask.objects.filter(name=task_name).first()

        # Create or get a CrontabSchedule that matches the reminder time
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=reminder_time.minute,
                hour=reminder_time.hour,
                day_of_month=reminder_time.day,
                month_of_year=reminder_time.month,
                day_of_week='*',
            )
                
            if periodic_task:
                periodic_task.crontab=schedule
                periodic_task.args = json.dumps([note.id])
                periodic_task.save()
                logger.info(f"Updated reminder task for note {note.id}")
                
            else:

            # Create a PeriodicTask to run the send_reminder task
                PeriodicTask.objects.create(
                    crontab=schedule,
                    name=task_name,
                    task='user.task.send_reminder',
                    args=json.dumps([note.id]),
                    one_off=True,
                )
            
        except Exception as e:
            logger.error(f"Error scheduling reminder: {str(e)}")
         

    def create(self, request, *args, **kwargs):
        """
        Create a new note for the logged-in user.
        """
        try:
            request.data.update(user=request.user.id)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            note_id = serializer.data['id']
        
        # Schedule the reminder if it exists
            if serializer.instance.reminder:
                self.sechdule_reminder(serializer.instance,request.data['reminder'])
            cache_key = f"user_{request.user.id}"
            cache_note = self.redis.get(cache_key)
            if cache_note is None:
                cache_note=[]
            cache_note.append(serializer.data)
            self.redis.save(cache_key,cache_note,ex=300)
            headers = self.get_success_headers(serializer.data)
            return Response({"Message":"The notes  is created of user ","satus":"Sucess","data":serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating note: {str(e)}")
            return Response({
                'error': 'An error occurred while creating the note.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Retrieve a specific note by its ID.
        """
        try:
            cache_key = f"user_{request.user.id}_note_{pk}"
            cache_note = self.redis.get(cache_key)
            if cache_note:
                logger.info(f"Notes are  fetched from the cache of user {cache_key}")
                return Response({"Message":"The data of the retrive note from cache","satus":"Sucess","data":cache_note},status=status.HTTP_200_OK)   
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            self.redis.save(cache_key, serializer.data, ex=300) 
            return Response({"Message":"The data of the retrive note","satus":"Sucess","data":serializer.data},status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving note with ID {pk}: {str(e)}")
            return Response({
                'error': 'An error occurred while retrieving the note.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Update a specific note by its ID.
        """
        try:
            
            # request.data.update(user=request.user.id)
            # user=request.user,collaborator__id=self.request.user.id
            # instance = self.get_object()
            instance = Note.objects.get(id=pk)
            if instance.user.id == request.user.id:
                data = request.data.copy()
                data['user'] = request.user.id
                
            else:
                collabrator = instance.collaborators_set.filter(user_id=request.user.id).first()
                
                if collabrator is None:
                    return Response({"Message":"You are not collaborator of this note","satus":"Error"},status=status.HTTP_403_FORBIDDEN)
                
                if collabrator.access_type == "read_only":
                    return Response({"Message":"You only have read_only permission on this note","satus":"Error"},status=status.HTTP_403_FORBIDDEN)
                    
                data = request.data.copy()
                data.pop('user',None)    
                        
            serializer = self.get_serializer(instance, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            # self.sechdule_reminder(pk)
            if serializer.instance.reminder:
                self.sechdule_reminder(serializer.instance,request.data['reminder'])
            note_cache_key = f"user_{request.user.id}_note_{pk}"
            self.redis.save(note_cache_key,serializer.data,ex=300)
            cache_key = f"user_{request.user.id}"
            queryset = self.get_queryset()
            self.redis.save(cache_key,self.get_serializer(queryset,many=True).data,ex=300)
            return Response({"Message":"The note is updated","satus":"Sucess","data":serializer.data},status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating note with ID {pk}: {str(e)}")
            return Response({
                'error': 'An error occurred while updating the note.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, *args, **kwargs):
        """
        Partially update a specific note by its ID.
        """
        try:
            
            
            # instance = Note.objects.get(id=pk,user=request.user,collaborator__id=self.request.user.id)
            instance = Note.objects.get(id=pk)
            # user=request.user,collaborator__id=self.request.user.id
            # instance = self.get_object()
            if instance.user.id == request.user.id:
                data = request.data.copy()
                data['user'] = request.user.id
                
            else:
                collabrator = instance.collaborators_set.filter(user_id=request.user.id).first()
                
                if collabrator is None:
                    return Response({"Message":"You are not collaborator of this note","satus":"Error"},status=status.HTTP_403_FORBIDDEN)
                
                if collabrator.access_type == "read_only":
                    return Response({"Message":"You only have read_only permission on this note","satus":"Error"},status=status.HTTP_403_FORBIDDEN)
                    
                data = request.data.copy()
                data.pop('user',None)    
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True) 
            self.perform_update(serializer)
            
            if serializer.instance.reminder:
                self.sechdule_reminder(serializer.instance,request.data['reminder'])
            note_cache_key = f"user_{request.user.id}_note_{pk}"
            self.redis.save(note_cache_key,serializer.data,ex=300)
            cache_key =  f"user_{request.user.id}"
            queryset=self.get_queryset()
            self.redis.save(cache_key,self.get_serializer(queryset,many=True).data,ex=300)
            return Response({"Message":"The note is partial updated","satus":"Sucess","data":serializer.data},status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error partially updating note with ID {pk}: {str(e)}")
            return Response({
                'error': 'An error occurred while partially updating the note.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Delete a specific note by its ID.
        """
        try:
            instance = Note.objects.get(id=pk)

            if instance.user.id == request.user.id:
                self.perform_destroy(instance)
                
                
            else:
                
                collabrator = instance.collaborators_set.filter(user_id=request.user.id).first()
                
                if collabrator is None:
                    return Response({"Message":"You are not collaborator of this note","satus":"Error"},status=status.HTTP_403_FORBIDDEN)
                
                if collabrator.access_type == "read_only":
                    return Response({"Message":"You only have read_only permission on this note","satus":"Error"},status=status.HTTP_403_FORBIDDEN)
                    
                self.perform_destroy(instance)
                
            
            note_cache_key = f"user_{request.user.id}_note_{pk}"
            
            self.redis.delete(note_cache_key)
            cache_key = f"user_{request.user.id}"
            queryset = self.get_queryset()
            self.redis.save(cache_key,self.get_serializer(queryset,many=True).data,ex=300)
            
            return Response({"Message":"The note is deleted","satus":"Sucess"},status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting note with ID {pk}: {str(e)}")
            return Response({
                'error': 'An error occurred while deleting the note.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='toggle_archive',url_name='toggle_archive', permission_classes=[IsAuthenticated])
    def toggle_archive(self, request, pk=None):
        """
        Toggle the archive status of a note.
        """
        try:
            note = Note.objects.get(id=pk)
            
            if note.user.id == request.user.id:
                note.is_archive = not note.is_archive
                
            else :
                collabrator = note.collaborators_set.filter(user_id=request.user.id).first()
                
                if collabrator is None:
                    return Response({"Message":"You are not collaborator of this note","satus":"Error"},status=status.HTTP_403_FORBIDDEN)
                
                if collabrator.access_type == "read_only":
                    return Response({"Message":"You only have read_only permission on this note","satus":"Error"},status=status.HTTP_403_FORBIDDEN)
                
                note.is_archive = not note.is_archive
                
            note.save()
            
            note_cache_key = f"user_{request.user.id}"
            
            note_cache_data = self.redis.get(note_cache_key)

            if note_cache_data:
                for cache_note in note_cache_data:
                    if cache_note['id'] == pk:           
                        cache_note['is_archive'] = note.is_archive
                self.redis.save(note_cache_key,note_cache_data,ex=300)
                logger.info(f"Note {pk} archive status toggled in cache bjjlfor user {request.user.id}")

            
            return Response({
                'message': 'Note archive status toggled successfully.',
                'data': NoteSerializer(note).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error toggling archive status for note with ID {pk}: {str(e)}")
            return Response({
                'error': 'An error occurred while toggling the archive status.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='archived_notes',url_name="archived_notes", permission_classes=[IsAuthenticated])
    def archived_notes(self, request):
        """
        List all archived notes for the logged-in user.
        """
        try:
            note_cache_key = f"user_{request.user.id}_archived_notes"
            note_cache_data = self.redis.get(note_cache_key)
            if note_cache_data:
                logger.info(f"Archived Notes feteched from the cache for user {request.user.id}")
                
        
                return Response({"Message":"Archived notes retrived from cache","satus":"Sucess","data":note_cache_data},status=status.HTTP_200_OK)   
                            
            queryset = Note.objects.filter(user=request.user, is_archive=True)
            serializer = NoteSerializer(queryset, many=True)
            self.redis.save(note_cache_key,serializer.data,ex=300)
            return Response({
                'message': 'Archived notes retrieved successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving archived notes: {str(e)}")
            return Response({
                'error': 'An error occurred while retrieving archived notes.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='toggle_trash', url_name='toggle_trash',permission_classes=[IsAuthenticated])
    def toggle_trash(self, request, pk=None):
        
        """
        Toggle the trash status of a note.
        """
        try:
            note = Note.objects.get(id=pk)
            if note.user.id == request.user.id:
                note.is_trash = not note.is_trash
                
            else :
                collabrator = note.collaborators_set.filter(user_id=request.user.id).first()
                
                if collabrator is None:
                    return Response({"Message":"You are not collaborator of this note","satus":"Error"},status=status.HTTP_403_FORBIDDEN)
                
                if collabrator.access_type == "read_only":
                    return Response({"Message":"You only have read_only permission on this note","satus":"Error"},status=status.HTTP_403_FORBIDDEN)
                
                note.is_trash = not note.is_trash
                
            note.save()
            
            note_cache_key = f"user_{request.user.id}"
            note_cache_data = self.redis.get(note_cache_key)
            if note_cache_data:
                for cache_note in note_cache_data:
                    if cache_note['id'] == pk:
                        cache_note['is_trash'] = note.is_trash
                self.redis.save(note_cache_key,note_cache_data,ex=300)
            return Response({
                'message': 'Note trash status toggled successfully.',
                'data': NoteSerializer(note).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error toggling trash status for note with ID {pk}: {str(e)}")
            return Response({
                'error': 'An error occurred while toggling the trash status.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='trashed_notes',url_name='trashed_notes', permission_classes=[IsAuthenticated])
    def trashed_notes(self, request):
        """
        List all trashed notes for the logged-in user.
        """
        try:
            note_cache_key = f"user_{request.user.id}"
            note_cache_data = self.redis.get(note_cache_key)
            if note_cache_data:
                logger.info(f"Trash note of user {request.user.id}")
                return Response({
                'message': 'Trashed notes retrieved from cache successfully.',
                'data': note_cache_data
            }, status=status.HTTP_200_OK)
                

            
            queryset = Note.objects.filter(user=request.user, is_trash=True)
            serializer = NoteSerializer(queryset, many=True)
            self.redis.save(note_cache_key,serializer.data,ex=300)
            return Response({
                'message': 'Trashed notes retrieved successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving trashed notes: {str(e)}")
            return Response({
                'error': 'An error occurred while retrieving trashed notes.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
            
    
class CollaboratorView(viewsets.ViewSet):
    
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    redis = RedisUtils()
    
    def get_queryset(self):
        return Collaborator.objects.filter(user=self.request.user)
    
    @swagger_auto_schema(
    operation_description="Add collaborator of the note API endpoint",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['note_id', 'user_id','access_type'],
        properties={
            'note_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the note'),
            'user_id': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='List of user IDs to add'),
            'access_type': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Type of access for the collaborator', 
                enum=['read_only', 'read_write']),
        }
    ),
    responses={
        200: 'Collaborator Added successfully',
        403: 'You are not the owner of this note',
        404: 'One or more labels not found',
        400: 'Invalid input',
    }
)       
  
    
    @action(detail=False, methods=['post'], url_path='add_collaborator',url_name='add_collaborator', permission_classes=[IsAuthenticated])
    def add_collaborator(self,request,*args, **kwargs):
      
        request.data.update(user=request.user.id)
            
        note_id = request.data.get('note_id')
        user_ids = request.data.get('user_id', [])
        access_type = request.data.get('access_type', Collaborator.read_only)

        try:
            # Retrieve the note object
            note = get_object_or_404(Note, id=note_id)

            # Check if the request user is the owner of the note
            if note.user != request.user:
                return Response({"error": "You are not the owner of this note."}, status=status.HTTP_403_FORBIDDEN)

            # Prepare data for the serializer
            collaborators_to_create = []

            users = User.objects.filter(id__in=user_ids)
            for user in users:
    
                if note.user == user:
                    return Response({"error": "The note owner cannot be added as a collaborator."}, status=status.HTTP_400_BAD_REQUEST)
                    

                # Add data to the list for bulk creation
                collaborators_to_create.append({
                    'note_id': note.id,
                    'user_id': user.id,
                    'access_type': access_type
                })
                
                
            serializer = CollaboratorSerializer(data=collaborators_to_create, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({"message": "Collaborators added successfully.","status":"Success","data":serializer.data}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error adding collaborator: {str(e)}")
            return Response({"error": "An error occurred while adding collaborators.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    @swagger_auto_schema(
    operation_description="remove collaborator of the note API endpoint",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['note_id', 'user_id'],
        properties={
            'note_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the note'),
            'user_id': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='List of user IDs to add'),
        }
    ),
    responses={
        200: 'Collaborator Remove successfully',
        403: 'You are not the owner of this note',
        404: 'One or more labels not found',
        400: 'Invalid input',
    }
)       
    @action(detail=False, methods=['post'], url_path='remove_collaborator',url_name='remove_collaborator', permission_classes=[IsAuthenticated])
       
    def remove_collaborator(self,request,*args, **kwargs):
        
        note_id = request.data.get('note_id')
        user_ids = request.data.get('user_id',[])
        
        note = Note.objects.filter(id=note_id).first()
        if not note:
            return Response({"error": "Note not found"}, status=status.HTTP_404_NOT_FOUND)
        
        Collaborator.objects.filter(note_id=note_id,user_id__in=user_ids).delete()
        
        return Response({"message":"Collaborator removed Successsfully"}, status=status.HTTP_204_NO_CONTENT)
    
class LabelsAddRemove(viewsets.ViewSet):
    
    """ This class is use to add and remove the notes"""
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    redis = RedisUtils()
    
    @swagger_auto_schema(
    operation_description="Add labels to a note",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['note_id', 'label'],
        properties={
            'note_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the note'),
            'label': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='List of label IDs to add'),
        }
    ),
    responses={
        200: 'Labels added successfully',
        403: 'You are not the owner of this note',
        404: 'One or more labels not found',
        400: 'Invalid input',
    }
)
    
    @action(detail=False,url_name="add_labels",url_path="add_labels",methods=['post'],permission_classes=[IsAuthenticated])
    def add_label(self, request, *args, **kwargs):
        try:
            request.data.update(user=request.user.id)
            note_id = request.data.get('note_id')
            label_id = request.data.get('label',[])
            
            note = Note.objects.filter(id=note_id).first()

            # Check if the request user is the owner of the note
            if note.user != request.user:
                return Response({"error": "You are not the owner of this note."}, status=status.HTTP_403_FORBIDDEN)

            # Prepare data for the serializer
            labels = Label.objects.filter(id__in=label_id).first()
            
            if labels is None:
                return Response({"error": "Label not found"}, status=status.HTTP_404_NOT_FOUND)
            
            for label in labels:
                if label.user.id != request.user.id:
                    return Response({"message":"Your not the owner of this label","status":"Error"},status=status.HTTP_403_FORBIDDEN)
                
            note.label.add(*labels)
            
            return Response({"message":"You added label Successfully","status":"Success"},status=status.HTTP_200_OK)
        
        except Exception as e:
            
            logger.error(f"Error adding Label: {str(e)}")

    
    
            return Response({"error": "An error occurred while adding Labels.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
   
   
    @swagger_auto_schema(
    operation_description="Remove labels to a note",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['note_id', 'label'],
        properties={
            'note_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the note'),
            'label': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='List of label IDs to add'),
        }
    ),
    responses={
        200: 'Labels remove successfully',
        403: 'You are not the owner of this note',
        404: 'One or more labels not found',
        400: 'Invalid input',
    }
)    
    @action(detail=False,methods=['post'],url_path="remove_labels",url_name="remove_labels",permission_classes=[IsAuthenticated])   
    def remove_label(self,request,*args, **kwargs):
        try:
            request.data.update(user=request.user.id)
            note_id = request.data.get('note_id')
            label_id = request.data.get('label',[])
            
            note = Note.objects.filter(id=note_id).first()
            
            if note.user.id != request.user.id:
                return Response({"message":"Your are not the owner of the label","status":"Error"},status=status.HTTP_403_FORBIDDEN)
            
            #Ensure that the label is exists
            labels = Label.objects.filter(id__in=label_id)
            if not labels.exists():
                return Response({"error": "One or more labels not found or not associated with this note."}, status=status.HTTP_404_NOT_FOUND)
            
            associated_labels = note.label.filter(id__in=label_id)
            if not associated_labels.exists():
                return Response({"error": "One or more labels are not associated with this note."}, status=status.HTTP_404_NOT_FOUND)


            # Remove the labels from the note
            note.label.remove(*associated_labels)

            return Response({"message": "Labels removed successfully", "status": "Success"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error while remove  Label: {str(e)}")
            return Response({"error": "An error occurred while remove Labels.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
            
            
            
            