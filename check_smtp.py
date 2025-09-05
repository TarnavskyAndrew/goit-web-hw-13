import smtplib, ssl
import asyncio
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from src.conf.config import settings


# Checking connection with SMTP service

server = settings.MAIL_SERVER
port = settings.MAIL_PORT

username = settings.MAIL_USERNAME
password = settings.MAIL_PASSWORD

context = ssl.create_default_context()

try:
    with smtplib.SMTP(server, port) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(username, password)
        print(">>>>> Successful login in SMTP")
except Exception as e:
    print("ERROR:", e)


# Checking credentials
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="Contacts API",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path("."),
)


async def test():
    message = MessageSchema(
        subject="Test Email",
        recipients=["your_real_email@gmail.com"],
        body="Hello! This is a test",
        subtype=MessageType.plain,
    )
    fm = FastMail(conf)
    await fm.send_message(message)


asyncio.run(test())
