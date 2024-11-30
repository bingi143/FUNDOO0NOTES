from django.shortcuts import render
from rest_framework import mixins,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
# from .utils import dictfetchall
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from .models import Label
from rest_framework import generics
from .serializers import LableSerialiser
from loguru import logger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import connection
# Create your views here.

class LabelView(mixins.CreateModelMixin,
                mixins.ListModelMixin,
                generics.GenericAPIView):
    
    
    
    queryset = Label.objects.all()
    serializer_class = LableSerialiser
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get_queryset(self):
        return Label.objects.filter(user=self.request.user)
    
    # @swagger_auto_schema(
    #     operation_description="Retrieve a list of labels or a single label by ID.",
    #     responses={200: LableSerialiser(many=True)},
    #     manual_parameters=[
    #         openapi.Parameter('pk', openapi.IN_PATH, description="Label ID", type=openapi.TYPE_INTEGER)
    #     ]  
    # )
    
    
    def get(self, request, *args, **kwargs):
                                                                                                 
        request.data.update(user=request.user.id) 
        try:
            if 'pk' in kwargs:
                return self.retrieve(request, *args, **kwargs)
            else:
                return self.list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error retrieving Label: {str(e)}")
            return Response({"error": "Error retrieving Label", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
     
    @swagger_auto_schema(
        operation_description="Create a new label.",
        request_body=LableSerialiser,
        responses={201: LableSerialiser}
    )
    def post(self,request,*args, **kwargs):
        
        try:
            request.data.update(user=request.user.id)
            serializer = LableSerialiser(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            headers = self.get_success_headers(serializer.data)
            # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            return self.create(request,*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error creating Label: {str(e)}")
            return Response({"error": "Error creating Label", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
class LabelViewMainu(
                mixins.RetrieveModelMixin,
                mixins.DestroyModelMixin,
                mixins.UpdateModelMixin,
                generics.GenericAPIView):
    
        
        
        queryset = Label.objects.all()
        serializer_class = LableSerialiser
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated]
        
        def get_queryset(self):
            return Label.objects.filter(user=self.request.user)
        
        
        def get(self, request, *args, **kwargs):
                                                                                                 
            request.data.update(user=request.user.id) 
            try:
                if 'pk' in kwargs:
                    return self.retrieve(request, *args, **kwargs)
                else:
                    return self.list(request, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error retrieving Label: {str(e)}")
                return Response({"error": "Error retrieving Label", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            

        
        
        @swagger_auto_schema(
            operation_description="Create a new label.",
            request_body=LableSerialiser,
            responses={200: LableSerialiser}
        )   
        def put(self,request,*args, **kwargs):
            
            try:
                request.data.update(user=request.user.id)
                self.update(request,*args, **kwargs)
                return Response({"message": "Label updated successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error updating Label: {str(e)}")
                return Response({
                    'error': 'An error occurred while Updating the note.',
                    'detail': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
                
                
        
        @swagger_auto_schema(
            operation_description="Create a new label.",
            request_body=LableSerialiser,
            responses={201: LableSerialiser}
        )       
        def patch(self,request,*args, **kwargs):
            try:
                request.data.update(user=request.user.id)
                self.partial_update(request,*args, **kwargs)
                return Response({"message": "Label partial updated successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error updating Label: {str(e)}")
                return Response({"error": "Error updating Label", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
                
        @swagger_auto_schema(
            operation_description="Delete a label by ID.",
            responses={204: "Label deleted successfully", 400: "Error deleting Label"}
        )    
        def delete(self, request, *args, **kwargs):
            """
            Delete a specific note by its ID.
            """
            try:
                request.data.update(user=request.user.id)
                self.destroy(request,*args, **kwargs)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                logger.error(f"Error deleting note with ID {request.user.id}: {str(e)}")
                return Response({
                    'error': 'An error occurred while deleting the note.',
                    'detail': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
                
                
                
                
                
class RawQueryView(
    generics.GenericAPIView, 
    mixins.ListModelMixin, 
    mixins.CreateModelMixin, 
    mixins.RetrieveModelMixin, 
    mixins.UpdateModelMixin, 
    mixins.DestroyModelMixin
):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_queryset(self):
        user_id = self.request.user.id
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM label WHERE user_id = %s", [user_id])
            rows = self.dictfetchall(cursor)
        return rows

    def perform_create(self, request):
        name = request.data.get('name')
        color = request.data.get('color')
        user_id = request.user.id

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO label (name, color, user_id) VALUES (%s, %s, %s) RETURNING id",
                [name, color, user_id]
            )
            row = cursor.fetchone()
        return row[0]

    def get(self, request, *args, **kwargs):
        try:
            if 'pk' in kwargs:
                label_id = kwargs['pk']
                user_id = request.user.id
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM label WHERE id = %s AND user_id = %s", [label_id, user_id])
                    row = self.dictfetchall(cursor)
                    if not row:
                        return Response({"error": "Label not found."}, status=status.HTTP_404_NOT_FOUND)
                    label = row[0]
                return Response(label)
            return Response(self.get_queryset())
        except Exception as e:
            logger.error(f"An error occurred while retrieving the label(s): {str(e)}")
            return Response({'error': 'An unexpected error occurred while retrieving the label(s).', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, *args, **kwargs):
            try:
                label_id = self.perform_create(request)
                return Response({"message": "Label created successfully.", "label_id": label_id}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating Label: {str(e)}")
                return Response({"error": "Error creating Label", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            
            
class RawQueryViewMain(
    generics.GenericAPIView, 
    mixins.ListModelMixin, 
    mixins.CreateModelMixin, 
    mixins.RetrieveModelMixin, 
    mixins.UpdateModelMixin, 
    mixins.DestroyModelMixin
):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_queryset(self):
        user_id = self.request.user.id
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM label WHERE user_id = %s", [user_id])
            rows = self.dictfetchall(cursor)
        return rows

    def perform_create(self, request):
        name = request.data.get('name')
        color = request.data.get('color')
        user_id = request.user.id

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO label (name, color, user_id) VALUES (%s, %s, %s) RETURNING id",
                [name, color, user_id]
            )
            row = cursor.fetchone()
        return row[0]

    def get(self, request, *args, **kwargs):
        try:
            if 'pk' in kwargs:
                label_id = kwargs['pk']
                user_id = request.user.id
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM label WHERE id = %s AND user_id = %s", [label_id, user_id])
                    row = self.dictfetchall(cursor)
                    if not row:
                        return Response({"error": "Label not found."}, status=status.HTTP_404_NOT_FOUND)
                    label = row[0]
                return Response(label)
            return Response(self.get_queryset())
        except Exception as e:
            logger.error(f"An error occurred while retrieving the label(s): {str(e)}")
            return Response({'error': 'An unexpected error occurred while retrieving the label(s).', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def put(self, request, *args, **kwargs):
            try:
                label_id = kwargs.get('pk')
                user_id = request.user.id

                name = request.data.get('name')
                color = request.data.get('color')

                # Ensure both name and color are provided
                if not name or not color:
                    return Response({"error": "Name and color are required fields."}, status=status.HTTP_400_BAD_REQUEST)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE label SET name = %s, color = %s WHERE id = %s AND user_id = %s RETURNING id",
                        [name, color, label_id, user_id]
                    )
                    row = cursor.fetchone()

                    if not row:
                        return Response({"error": "Label not found or not yours to update."}, status=status.HTTP_404_NOT_FOUND)

                return Response({"message": "Label updated successfully."}, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Error updating Label: {str(e)}")
                return Response({"error": "Error updating Label", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)   

    def delete(self, request, *args, **kwargs):
        try:
            label_id = kwargs.get('pk')
            user_id = request.user.id
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM label WHERE id = %s AND user_id = %s RETURNING id", [label_id, user_id])
                row = cursor.fetchone()
                if not row:
                    return Response({"error": "Label not found or not yours to delete."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Label deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting Label: {str(e)}")
            return Response({"error": "Error deleting Label", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
