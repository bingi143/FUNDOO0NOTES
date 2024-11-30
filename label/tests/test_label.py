import pytest
from user.models import User
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken



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
@pytest.mark.labels_success
class TestLabels :
  
    def test_create_labels(self, client, generate_usertoken):
        label_data ={"name":"the book",
                        "color":"black"
                        }
        
        url = reverse('label')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',data=label_data,content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        return response.data['id']
        
    def test_create_labels_missing_fielf(self, client, generate_usertoken):
        label_data ={}
        
        url = reverse('label')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',data=label_data,content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
        
    def test_label_create_number_data(self, client, generate_usertoken):
        data = {
            "name": 123,
            "color": "Yellow"
        }
        url = reverse('label')
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        
    def test_label_create_unautho(self, client):
        data = {
            "name": "Cr7",
            "color": "Yellow"
        }
        url = reverse('label')
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        
    # Retrive all labels   list
        
    def test_get_all_labels(self,client,generate_usertoken):
        url = reverse('label')
        response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',content_type='application/json')
        response_data=response.json()
        print(f"response_data:{response_data}")
        assert response.status_code == status.HTTP_200_OK

    def test_get_all_labels_unautho(self, client):
        url = reverse('label')
        response = client.get(url, content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        
    #update labels
    def test_update_label(self,client,generate_usertoken):
        
        label_id = self.test_create_labels(client,generate_usertoken)
        data = {
            "name":"Cr7777777777",
            "color":"Yellow"
        }
        url = reverse('label_main', args=[label_id])
        response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        assert response.status_code == status.HTTP_200_OK

    def test_update_label_invalid_data(self, client, generate_usertoken):
        label_id = self.test_create_labels(client, generate_usertoken)
        data = {
            "name": "",
            "color": "Yellow"
        }
        url = reverse('label_main', args=[label_id])
        response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_label_not_found(self, client, generate_usertoken):
        invalid_label_id = 9999
        data = {
            "name": "Cr7777777777",
            "color": "Yellow"
        }
        url = reverse('label_main', args=[invalid_label_id])
        response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # print("Update label not found response:", response.data)

    def test_update_label_unauthenticated(self, client):
        """
        Test updating a label without being authenticated.
        """
        label_id = 1 
        data = {
            "name": "Cr7777777777",
            "color": "Yellow"
        }
        url = reverse('label_main', args=[label_id])
        response = client.put(url, data=data, content_type='application/json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        print("Update label unauthenticated response:", response.data)

    
    #DELETE Label
    def test_destory_label(self,client,generate_usertoken):
        label_id = self.test_create_labels(client, generate_usertoken)
        
        url = reverse('label_main', args=[label_id])
        response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    
    def test_destroy_label_not_found(self, client, generate_usertoken):
        invalid_label_id = 9999
        url = reverse('label_main', args=[invalid_label_id])
        response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        

    def test_destroy_label_by_unauthorized_user(self,client, generate_usertoken, generate_usertoken2):
        # First, create a label using an authorized user
        label_id = self.test_create_labels(client, generate_usertoken)
        
        # Attempt to delete the label using a different, unauthorized user
        url = reverse('label_main', args=[label_id])
        response = client.delete(
            url, 
            HTTP_AUTHORIZATION=f'Bearer {generate_usertoken2}', 
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
