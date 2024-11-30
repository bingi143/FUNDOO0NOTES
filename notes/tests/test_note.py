import pytest
from user.models import User
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


#Create Note Pytest
@pytest.fixture
def generate_usertoken(client, django_user_model):
    django_user_model.objects.create_user(
        # first_name="Sonal",
        # last_name="Rajupt",
        email="sonalraj2001@gmail.com",
        password="Sonal@2002"
    )

    data = {
       "email":"sonalraj2001@gmail.com",
       "password":"Sonal@2002",
    }
    url = reverse('login_user')
    response = client.post(url, data=data, content_type='application/json')
    # print(f"res  : {response.data}")
    return response.data["data"]["access"]


@pytest.fixture
def generate_usertoken2(client, django_user_model):
    django_user_model.objects.create_user(
        # first_name="Sonal",
        # last_name="Rajupt",
        email="sonalraj2002@gmail.com",
        password="Sonal@2002"
    )

    data = {
       "email":"sonalraj2002@gmail.com",
       "password":"Sonal@2002",
    }
    url = reverse('login_user')
    response = client.post(url, data=data, content_type='application/json')
    # print(f"res  : {response.data}")
    return response.data["data"]["access"]


@pytest.mark.django_db
@pytest.mark.note
class TestNoteSuccess:
    
    # @pytest.fixture
    def test_note_create(self,client,generate_usertoken):
        
        data = {
    "title": "Meeting",
    "description": "This is the description of my secret note.",
    "color": "violet",
    "is_archive": True,
    "is_trash": False,
    "reminder":"2024-08-26T11:50"
}
        url = reverse('note-list')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',data=data,content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        # assert 'id' in response.data
        # print(response.data['data'])  
        return response.data['data']['id']

    def test_note_create_by_2user(self,client,generate_usertoken2):
        
        data = {
    "title": "Meeting",
    "description": "This is the description of my secret note.",
    "color": "violet",
    "is_archive": True,
    "is_trash": False,
    "reminder":"2024-08-26T11:50"
}
        url = reverse('note-list')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken2}',data=data,content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        # assert 'id' in response.data
        # print(response.data['data'])  
        return response.data['data']['user']
    
    
    def test_note_list(self,client,generate_usertoken):
        
        url = reverse('note-list')
        response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        
        
    def test_update_note(self,client,generate_usertoken):
        
        note_id = self.test_note_create(client,generate_usertoken)
        data = {
        "title": "Meeting",
        "description": "Updated description",
        "reminder": "2024-08-26T11:50"
           }
        url = reverse('note-detail', args=[note_id])
        response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK
        
        
    def test_parital_update_note(self,client,generate_usertoken):
            
        note_id = self.test_note_create(client,generate_usertoken)
        data = {
        "title": "Meeting",
        "description": "Updated description",
        "is_archive": True, 
        "is_trash": True,
        "reminder": "2024-08-26T11:50"
           }
        url = reverse('note-detail', args=[note_id])
        response = client.patch(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK   
    
        
    def test_destory_create(self,client,generate_usertoken):
        note_id = self.test_note_create(client,generate_usertoken)
        
        url = reverse('note-detail', args=[note_id])
        response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK   
        
       
        
    def test_toggle_archive(self,client,generate_usertoken):
        note_id = self.test_note_create(client,generate_usertoken)
        
        url = reverse('note-toggle_archive', args=[note_id])
        response = client.patch(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK
        
    def test_toggle_trash(self,client,generate_usertoken):
        note_id = self.test_note_create(client,generate_usertoken)
        
        url= reverse('note-toggle_trash',args=[note_id])
        response = client.patch(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
    
    
    def test_archive_notes(self,client,generate_usertoken):
        
        url = reverse('note-archived_notes')
        response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        
        
    def test_trash_notes(self,client,generate_usertoken):
        
        url = reverse('note-trashed_notes')
        response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        
    # def test_restive_note(self,client,generate_usertoken):
    #     note_id = self.test_note_create(client,generate_usertoken)
    #     print(type(note_id))
        
    #     url =  reverse('note-detail',args=[1])
    #     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
    #     print('resp',response)
    #     assert response.status_code == status.HTTP_200_OK
        
        
        
        
@pytest.mark.django_db
@pytest.mark.note_cr_exceptions
class TestNoteCreateFailure:
    
    def test_note_create_without_token(self,client):
        
        data = {
    "title": "Meeting",
    "description": "This is the description of my secret note.",
    "color": "violet",
    "is_archive": True,
    "is_trash": False,
    "reminder":"2024-08-26T11:50"
}
        url = reverse('note-list')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',data=data,content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
            
            
    def test_note_create_missing_title(self,client, generate_usertoken):
        data = {
        "description": "This is a note without a title.",
        "color": "blue",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-08-26T11:50"
    }
        url = reverse('note-list')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # assert 'title' in response.data
        
    def test_note_create_invalid_reminder(self, client, generate_usertoken):
        data = {
        "title": "Invalid Reminder",
        "description": "This note has an invalid reminder field.",
        "color": "green",
        "is_archive": False,
        "is_trash": False,
        "reminder": "invalid-date-time"
    }
        url = reverse('note-list')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
           
        
    def test_note_create_empty_payload(self, client, generate_usertoken):
        data = {}
        url = reverse('note-list')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
@pytest.mark.django_db
@pytest.mark.note_list_exceptions
class TestNoteListFailure:
    
    def test_note_list_unauthorized(self, client):
        url = reverse('note-list')
        response = client.get(url, content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED   
        
    def test_note_list_invalid_url(self, client, generate_usertoken):
        url = '/invalid-url/'
        response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_note_list_invalid_method(self, client, generate_usertoken):
        url = reverse('note-list')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.note_update_exceptions
class TestNoteUpdateFailure(TestNoteSuccess):
    
    def test_update_note_missing_fields(self, client, generate_usertoken):
        note_id = super().test_note_create(client, generate_usertoken)
        data = {
            "title": "Updated Meeting"  # Missing 'description' and 'reminder'
        }
        url = reverse('note-detail', args=[note_id])
        response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_update_note_unauthorized(self, client):
        note_id = 1  # Assuming a note with ID 1 exists
        data = {
            "title": "Meeting",
            "description": "Updated description",
            "reminder": "2024-08-26T11:50"
        }
        url = reverse('note-detail', args=[note_id])
        response = client.put(url, data=data, content_type='application/json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        
    def test_update_note_invalid_id(self, client, generate_usertoken):
        invalid_note_id = 9999  # Assuming this note ID does not exist
        data = {
            "title": "Meeting",
            "description": "Updated description",
            "reminder": "2024-08-26T11:50"
        }
        url = reverse('note-detail', args=[invalid_note_id])
        response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
    
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_update_note_invalid_data_type(self, client, generate_usertoken):
        note_id = self.test_note_create(client, generate_usertoken)
        data = {
            "title": 123,  # Title should be a string, not an integer
            "description": "Updated description",
            "reminder": "Invalid Date Format"  # Invalid date format
        }
        url = reverse('note-detail', args=[note_id])
        response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.note_delete_exceptions
class TestNoteDeleteFailure:
    
    def test_note_create(self, client, generate_usertoken):
        data = {
            "title": "Meeting",
            "description": "This is the description of my secret note.",
            "color": "violet",
            "is_archive": True,
            "is_trash": False,
            "reminder": "2024-08-26T11:50"
        }
        url = reverse('note-list')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        return response.data['data']['id']
    
    def test_destroy_note_not_exists(self, client, generate_usertoken):
        # Attempt to delete a note with an ID that does not exist
        nonexistent_note_id = 99999
        url = reverse('note-detail', args=[nonexistent_note_id])
        response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST  # Use 404 for non-existent resources
        
        
    def test_destroy_note_by_unauthrised(self, client, generate_usertoken,generate_usertoken2):
            # Attempt to delete a note with an ID that does not exist
        note_id = self.test_note_create(client,generate_usertoken)
        url = reverse('note-detail', args=[note_id])
        response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken2}', content_type='application/json')
        assert response.status_code == status.HTTP_403_FORBIDDEN  # Use 404 for non-existent resources
        
   
@pytest.mark.django_db
@pytest.mark.note_toggle_fail
class TestNoteToggleFailure:
    
    def test_toggle_archive_nonexistent_note(self, client, generate_usertoken):
        # Attempt to toggle the archive status of a note that does not exist
        nonexistent_note_id = 99999
        url = reverse('note-toggle_archive', args=[nonexistent_note_id])
        response = client.patch(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST 
    
    def test_toggle_trash_nonexistent_note(self, client, generate_usertoken):
        # Attempt to toggle the trash status of a note that does not exist
        nonexistent_note_id = 99999
        url = reverse('note-toggle_trash', args=[nonexistent_note_id])
        response = client.patch(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST 
    
    def test_archive_notes_without_authentication(self, client):
        # Attempt to fetch archived notes without including the Authorization header
        url = reverse('note-archived_notes')
        response = client.get(url, content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    def test_trash_notes_without_authentication(self, client):
        # Attempt to fetch trashed notes without including the Authorization header
        url = reverse('note-trashed_notes')
        response = client.get(url, content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.note_collab   


class TestCollab(TestNoteSuccess):

    def test_collab_add(self, client, generate_usertoken, generate_usertoken2):
        # Attempt to add a collaborator to a note
        note_id = self.test_note_create(client, generate_usertoken)
        user_id = self.test_note_create_by_2user(client, generate_usertoken2)
        
        
        data = {
            "note_id": note_id,
            "user_id": [user_id],  # Use the user ID instead of the token
            "access_type": "read_write"
        }
        
        url = reverse('collab-add_collaborator')
        response = client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        
        assert response.status_code == status.HTTP_201_CREATED
     
        
        
    def test_collab_add_unauthorized(self, client, generate_usertoken2, generate_usertoken):
        # Attempt to add a collaborator by a user who is not the owner of the note
        note_id = self.test_note_create(client, generate_usertoken)
        
        user1 = User.objects.create(email="user1@example.com", password="password123")
        
        data = {
            "note_id": note_id,
            "user_id": [user1.id],  # Use the user ID instead of the token
            "access_type": "read_write"
        }
        
        url = reverse('collab-add_collaborator')
        response = client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken2}', content_type='application/json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        # assert response.data["message"] == "You are not authorized to add collaborators to this note."

    def test_collab_add_owner_as_collaborator(self, client, generate_usertoken):
        # Attempt to add the note owner as a collaborator
        note_id = self.test_note_create(client, generate_usertoken)
        
        owner = User.objects.create(email="owner@example.com", password="password123")
        
        data = {
            "note_id": note_id,
            "user_id": [owner.id],  # Use the owner's user ID
            "access_type": "read_write"
        }
        
        url = reverse('collab-add_collaborator')
        response = client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        
        
    def test_collab_remove(self, client, generate_usertoken, generate_usertoken2):
        # Attempt to add a collaborator to a note
        note_id = self.test_note_create(client, generate_usertoken)
        user_id = self.test_note_create_by_2user(client, generate_usertoken2)
        
        
        data = {
            "note_id": note_id,
            "user_id": [user_id],  # Use the user ID instead of the token   
        }
        
        url = reverse('collab-remove_collaborator')
        response = client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        
    
        
    def test_collab_remove_by_unauthorized(self, client, generate_usertoken2, generate_usertoken):
        # Attempt to add a collaborator by a user who is not the owner of the note
        note_id = self.test_note_create(client, generate_usertoken)
        
        user1 = User.objects.create(email="user1@example.com", password="password123")
        
        data = {
            "note_id": note_id,
            "user_id": [user1.id],  # Use the user ID instead of the token
        
        }
        
        url = reverse('collab-add_collaborator')
        response = client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken2}', content_type='application/json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    
    
    
    
@pytest.mark.django_db
@pytest.mark.coll
class TestAddCollaborators:

    def test_note_create(self,client,generate_usertoken):
        data = {
            "title": "Meeting",
            "description": "This is the description of my secret note.",
            "color": "violet",
            "is_archive": True,
            "is_trash": False,
            "reminder":"2024-08-26T11:50"
        }
        url = reverse('note-list')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',data=data,content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        print("NOTE ID=",response.data["data"]["id"])
        return response.data["data"]["id"]
    

    def test_label_create(self,client,generate_usertoken):
        data = {
            "name":"Cr7",
            "color":"Yellow"
        }
        url = reverse('label')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',data=data,content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        print("LABEL ID=",response.data["id"])
        return response.data["id"]

    def test_add_labels_success(self, client, generate_usertoken):
        """
        Test case to successfully add labels to a note.
        """
        note_id = self.test_note_create(client, generate_usertoken)  
        label_id = self.test_label_create(client, generate_usertoken)  
        
        url = reverse('labels-add_labels') 
        data = {
            "note_id": note_id,
            "label_ids": [label_id]
        }
        response = client.post(url, data=data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')

        assert response.status_code == status.HTTP_200_OK
        # assert "Labels added successfully" in response.data["message"]  
        # print("Success response:", response.data)

    def test_add_labels_note_not_found(self, client, generate_usertoken):
        """
        Test case for adding labels to a note that does not exist.
        """
        url = reverse('labels-add_labels')
        data = {
            "note_id": 9999, 
            "label_ids": [1]
        }
        response = client.post(url, data=data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # assert "Note not found" in response.data["error"] 
        # print("Error response:", response.data)

    def test_add_labels_not_owner(self, client, generate_usertoken,generate_usertoken2):
        """
        Test case for adding labels to a note where the user is not the owner of the note.
        """
        note_id = self.test_note_create(client, generate_usertoken2)  

        label_id = self.test_label_create(client, generate_usertoken2)  
        
        url = reverse('labels-add_labels')
        data = {
            "note_id": note_id,
            "label_ids": [label_id]
        }
        response = client.post(url, data=data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        # assert "You are not the owner of this note." in response.data["error"] 
        # print("Error response:", response.data)

    def test_add_labels_no_valid_labels(self, client, generate_usertoken):
        """
        Test case for adding labels where no valid labels are provided.
        """
        note_id = self.test_note_create(client, generate_usertoken) 
        
        url = reverse('labels-add_labels')
        data = {
            "note_id": note_id,
            "label_ids": [9999] 
        }
        response = client.post(url, data=data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')

        assert response.status_code == status.HTTP_404_NOT_FOUND



    def create_note_and_label(self, client, generate_usertoken):
        """
        Utility function to create a note and a label, then return their IDs.
        """
        note_data = {
            "title": "Meeting",
            "description": "This is the description of my secret note.",
            "color": "violet",
            "is_archive": True,
            "is_trash": False,
            "reminder": "2024-08-26T11:50"
        }
        note_url = reverse('note-list')
        note_response = client.post(note_url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=note_data, content_type='application/json')
        assert note_response.status_code == status.HTTP_201_CREATED
        note_id = note_response.data["data"]["id"]

        label_data = {
            "name": "Cr7",
            "color": "Yellow"
        }
        label_url = reverse('label')
        label_response = client.post(label_url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=label_data, content_type='application/json')
        assert label_response.status_code == status.HTTP_201_CREATED
        label_id = label_response.data["id"]

        return note_id, label_id

    def add_label_to_note(self, client, generate_usertoken, note_id, label_id):
        """
        Utility function to add a label to a note.
        """
        add_url = reverse('labels-add_labels')
        add_data = {
            "note_id": note_id,
            "label_ids": [label_id]
        }
        add_response = client.post(add_url, data=add_data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert add_response.status_code == status.HTTP_200_OK
        # assert "Labels added successfully" in add_response.data["message"]
        # print("Label added to note:", add_response.data)

    # def test_add_labels_success(self, client, generate_usertoken):
    #     """
    #     Test case to successfully add labels to a note.
    #     """
    #     note_id, label_id = self.create_note_and_label(client, generate_usertoken)
    #     self.add_label_to_note(client, generate_usertoken, note_id, label_id)
        
        
        # url = reverse('labels-add_labels')
        # response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='applicaton/json')

    # def test_remove_labels_success(self, client, generate_usertoken):
    #     """
    #     Test case to successfully remove labels from a note.
    #     """
    #     note_id, label_id = self.create_note_and_label(client, generate_usertoken)

    #     self.add_label_to_note(client, generate_usertoken, note_id, label_id)

    #     remove_url = reverse('labels-remove_labels')
    #     remove_data = {
    #         "note_id": note_id,
    #         "label_ids": [label_id]
    #     }
    #     remove_response = client.post(remove_url, data=remove_data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')

    #     assert remove_response.status_code == status.HTTP_200_OK       # assert "Labels removed successfully" in remove_response.data["message"]
        # print("Label removed from note:", remove_response.data)


    def test_remove_labels_not_owner(self, client, generate_usertoken, generate_usertoken2):
        """
        Test case to ensure a user cannot remove labels from a note they don't own.
        """
        note_id, label_id = self.create_note_and_label(client, generate_usertoken2) 

        remove_url = reverse('labels-remove_labels')
        remove_data = {
            "note_id": note_id,
            "label_ids": [label_id]
        }
        remove_response = client.post(remove_url, data=remove_data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')

        assert remove_response.status_code == status.HTTP_403_FORBIDDEN
        # assert "You are not the owner of this note." in remove_response.data["error"]

    # def test_remove_non_existent_label(self, client, generate_usertoken):
    #     """
    #     Test case for attempting to remove a non-existent label from a note.
    #     """
    #     note_id, label_id = self.create_note_and_label(client, generate_usertoken)

    #     self.add_label_to_note(client, generate_usertoken, note_id, label_id)

    #     non_existent_label_id = label_id + 1 
    #     remove_url = reverse('labels-remove_labels')
    #     remove_data = {
    #         "note_id": note_id,
    #         "label_ids": [non_existent_label_id]
    #     }
    #     remove_response = client.post(remove_url, data=remove_data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')

    #     assert remove_response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_remove_labels_not_assigned(self, client, generate_usertoken):
        """
        Test case for attempting to remove a label that isn't assigned to the note.
        """
        note_id, label_id = self.create_note_and_label(client, generate_usertoken)

        remove_url = reverse('labels-remove_labels')
        remove_data = {
            "note_id": note_id,
            "label_ids": [label_id]
        }
        remove_response = client.post(remove_url, data=remove_data, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')

        assert remove_response.status_code == status.HTTP_404_NOT_FOUND
    
