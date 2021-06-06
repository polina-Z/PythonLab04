from enum import Enum
import threading
from django.core.mail import send_mail
import logging
import smtplib


logger = logging.getLogger(__name__)


class Status(Enum):
    ACTIVE = 2
    FINISHED = 1
    FAILED = 0

    def __str__(self):
        return str(self.name).lower()


class Priority(Enum):
    HIGH = 2
    NORMAL = 1
    LOW = 0

    def __str__(self):
        return str(self.name).lower()


class SendToEmail(threading.Thread):
    def __init__(self, email, username):
        self.email = email
        self.username = username
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                "Добро пожаловать на сайт TaskManager",
                "Здравствуйте {}! Благодарим вас за регистрацию на сайте TaskManager.".format(
                    self.username
                ),
                "djangotaskmanager@mail.ru",
                ["{}".format(self.email)],
                fail_silently=False,
            )
        except Exception as ex:
            logging.error("Сообщение не было отправлено. {}".format(ex))
