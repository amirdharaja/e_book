from django.conf import settings
from django.core.mail import send_mail
import threading

username = settings.EMAIL_USERNAME


def send_email(recipient, subject, content):
    Email(subject, content, username, recipient).start()

class Email(threading.Thread):
    def __init__(self, subject, content, username, recipient):
        self.subject = subject
        self.recipient = (recipient,)
        self.content = content
        self.sender = username
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.content, self.sender, self.recipient)
