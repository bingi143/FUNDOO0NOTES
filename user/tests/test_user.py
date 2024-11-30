
import pytest
from user.models import User
from rest_framework.reverse import reverse
from rest_framework import status
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


#User Resigtration Pytest
@pytest.mark.django_db
@pytest.mark.register_success
def test_user_registration(client):
    data = {"first_name":"Pinky",
"last_name": "Yadav",
"email":"pinky1995@gmail.com",
"password":"Pinky564"}
    
    url = reverse('register_user')
    response = client.post(url,data,content_type='application/json')
    assert response.status_code == 200
    
@pytest.mark.django_db
@pytest.mark.userexist
def test_exists_user_registration(client):
    data = {"first_name":"Pinky",
"last_name": "Yadav",
"email":"pinky1995@gmail.com",
"password":"Pinky564"}
    
    url = reverse('register_user')
    response = client.post(url,data,content_type='application/json')
    response = client.post(url,data=data,content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
@pytest.mark.django_db
@pytest.mark.register_missi
def test_user_registration_missing_field(client):
    # Data missing required fields
    data = {
        "first_name": "Pinky",
        "email": "pinky1995@gmail.com",
        "password": "Pinky564"
    }
    
    url = reverse('register_user')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.invalid_email
def test_user_registration_invalid_email(client):
    data = {"first_name":"Pinky",
"last_name": "Yadav",
"email":"pinkyemail",
"password":"Pinky564"}
    
    url = reverse('register_user')
    response = client.post(url,data,content_type='application/json')
    assert response.status_code == 400
    

@pytest.mark.django_db
@pytest.mark.invalid_password
def test_user_registration_invalid_password(client):
    data = {"first_name":"Pinky",
"last_name": "Yadav",
"email":"pinky1995@gmail.com",
"password":"Pinky5"}
    
    url = reverse('register_user')
    response = client.post(url,data,content_type='application/json')
    assert response.status_code == 400 

@pytest.mark.django_db
@pytest.mark.register_nodata
def test_user_registration_no_data(client):
    data = {}
    
    url = reverse('register_user')
    response = client.post(url,data,content_type='application/json')
    assert response.status_code == 400
        
#User Login 

@pytest.mark.django_db
@pytest.mark.login
def test_user_login(client):
    user = User.objects.create_user(email='pinky1995@gmail.com', password='Pinky564')
    login_data = {"email":"pinky1995@gmail.com",
"password":"Pinky564"}
    url = reverse('login_user')
    response = client.post(url,login_data,content_type='application/json')
    assert response.status_code == 200
    


@pytest.mark.django_db
@pytest.mark.login_password
def test_user_login_invalid_password(client):
    user = User.objects.create_user(email='pinky1995@gmail.com', password='Pinky564')
    login_data = {"email":"pinky1995@gmail.com",
"password":"Pinky554"}
    url = reverse('login_user')
    response = client.post(url,login_data,content_type='application/json')
    assert response.status_code == 400

@pytest.mark.django_db
@pytest.mark.login_email
def test_user_login_invalid_email(client):
    user = User.objects.create_user(email='pinky1995@gmail.com', password='Pinky564')
    login_data = {"email":"pinky1999@gmail.com",
"password":"Pinky564"}
    url = reverse('login_user')
    response = client.post(url,login_data,content_type='application/json')
    assert response.status_code == 400

@pytest.mark.django_db
@pytest.mark.login_missing
def test_user_login_missing_field(client):
    user = User.objects.create_user(email='pinky1995@gmail.com', password='Pinky564')
    login_data = {"email":"pinky1995@gmail.com"}
    url = reverse('login_user')
    response = client.post(url,login_data,content_type='application/json')
    assert response.status_code == 400
    
@pytest.mark.django_db
@pytest.mark.login_exists
def test_user_login_dont_exists(client):
    # user = User.objects.create_user(email='pinky1995@gmail.com', password='Pinky564')
    login_data = {"email":"pinky1995@gmail.com",
"password":"Pinky564"}
    url = reverse('login_user')
    response = client.post(url,login_data,content_type='application/json')
    assert response.status_code == 400
    
#User Email_Verify Pytest
@pytest.mark.django_db
@pytest.mark.email_verify
def test_verify_user(client):
    User = get_user_model()  # Get the custom user model
    
  
    user = User.objects.create_user(
        first_name="Vinit",
        last_name="Bhamare",
        email="ombhamare2001@gmail.com",
        password="Vinit@2002"
    ) 
    # Step 2: Obtain JWT Token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Step 3: Create verification URL with the token
    url = reverse('verify_email', kwargs={'token': access_token})
    
    # Step 4: Send the verification request
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {access_token}', content_type='application/json')   
    # Step 5: Check if the verification was successful
    assert response.status_code == 200  
    
    # Optional: Check if the user's `is_verified` status is now True
    user.refresh_from_db()  # Refresh the user's data from the database
    assert user.is_verified is True 


