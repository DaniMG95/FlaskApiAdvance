from typing import List
from requests import Response, post
import os

class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
    FROM_TITLE = "Store REST API"
    FROM_EMAIL = f"mailgun@{MAILGUN_DOMAIN}"

    @classmethod
    def send_confirmation_email(cls, email: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailGunException("Need Api Key Mailgun")
        if cls.MAILGUN_DOMAIN is None:
            raise MailGunException("Need domain Mailgun")
        response = post(
            f"http://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html
            },
        )
        if response.status_code != 200:
            raise MailGunException("Error to send confirmation email")
        return response