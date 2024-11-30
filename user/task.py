from __future__ import absolute_import,unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
# from time import sleep
from notes.models import Note
from loguru import logger


@shared_task
def send_email_task(email_subject, email_body, recipient_email):
    send_mail(
        subject=email_subject,
        message=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )

    
@shared_task
def send_reminder(note_id):
    try:
        note = Note.objects.get(id=note_id)
        user_email = note.user.email
        body=f"Reminder for Note: {note.title} - {note.reminder}"
        subject = f"Reminder"
        send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    except Exception as e:
        logger.info("Note not found")
    
    
