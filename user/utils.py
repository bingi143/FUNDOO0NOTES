import re
from django.core.mail import EmailMessage

# Example regex patterns
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Valid email format
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'  # Minimum 8 chars, at least one letter and one number

def is_valid_email(email):
    if re.match(EMAIL_REGEX, email):
        return False
    return True

def is_valid_password(password):
    if re.match(PASSWORD_REGEX, password):
        return False
    
    return True
   

def is_validate_name(name):
    # Example regex for name validation: only allows letters and spaces
    NAME_REGEX = r'^[A-Za-z\s]+$'
    if  re.match(NAME_REGEX, name):
        return False
    return True


# def send_mail(data):
#     email = EmailMessage(subject=data['email_subject'],body=data['email_body'],to=[data('to_email')])
#     email.send()