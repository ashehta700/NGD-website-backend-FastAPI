from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
from app.utils.paths import static_path

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


# -------------------------
# Mail Configuration
# -------------------------
SMTP_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("MAIL_PORT", 587))
SMTP_USERNAME = os.getenv("MAIL_USERNAME")
SMTP_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM", SMTP_USERNAME)
SYSTEM_EMAIL = os.getenv("SYSTEM_EMAIL", SMTP_USERNAME)
MAIL_TLS = os.getenv("MAIL_TLS", "True").lower() == "true"
MAIL_SSL = os.getenv("MAIL_SSL", "False").lower() == "true"

# -------------------------
# File Directories
# -------------------------
CONTACT_DIR = static_path("contact", ensure=True)
REQUEST_DIR = static_path("requests", ensure=True)
ADMIN_UPLOAD_DIR = static_path("requests", "reply", ensure=True)

# -------------------------
# Email Helper Functions
# -------------------------
def _send_raw_email(msg, to_email: str):
    """Low-level helper for sending emails via SMTP."""
    if MAIL_SSL:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    else:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        if MAIL_TLS:
            server.starttls()

    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(MAIL_FROM, [to_email], msg.as_string())
    server.quit()

def send_email(subject: str, body: str, to_email: str):
    msg = MIMEMultipart()
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    _send_raw_email(msg, to_email)
    print(f"✅ Email sent to {to_email}")

def send_email_with_attachment(subject: str, body: str, to_email: str, attachment_rel: str):
    msg = MIMEMultipart()
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    # Build full path to the attachment
    full_path = static_path(attachment_rel)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Attachment not found: {full_path}")

    with open(full_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(full_path)}")
    msg.attach(part)

    _send_raw_email(msg, to_email)
    print(f"✅ Email with attachment sent to {to_email}")

# -------------------------
# Background Email Tasks
# -------------------------
def send_request_email(request_number: str, category: str, user_email: str, first_name: str, background_tasks: BackgroundTasks):
    subject = f"NGD - Your {category} request has been received"
    body = f"""
    <p>Dear {first_name},</p>
    <p>We have received your <strong>{category}</strong> request with number <strong>{request_number}</strong>.</p>
    <p>Our team will review it and respond as soon as possible.</p>
    <p>Thank you for your submission.</p>
    """
    background_tasks.add_task(send_email, subject, body, user_email)

    # also notify system admin
    admin_subject = f"New Request Submitted: {request_number}"
    admin_body = f"<p>A new request has been submitted for category <b>{category}</b>.</p>"
    background_tasks.add_task(send_email, admin_subject, admin_body, SYSTEM_EMAIL)

def send_reply_email(request_number: str, user_email: str, reply_body: str, background_tasks: BackgroundTasks):
    subject = f"NGD - Response to your request {request_number}"
    body = f"""
    <p>Dear user,</p>
    <p>We have responded to your request <strong>{request_number}</strong>:</p>
    <p>{reply_body}</p>
    <p>Thank you for using our system.</p>
    """
    background_tasks.add_task(send_email, subject, body, user_email)







# ----------------------------------------------
##################################################3
# test with   mailersend for test
# # utils/email.py
# from fastapi import BackgroundTasks
# from mailersend import MailerSendClient, EmailBuilder
# import os
# from dotenv import load_dotenv
# from typing import List, Optional

# # Load environment variables from .env (MAILERSEND_API_KEY)
# load_dotenv()

# # Initialize MailerSend client
# ms = MailerSendClient()


# def send_email(subject: str, body: str, to_email: str, to_name: Optional[str] = None):
#     """
#     Send a simple email via MailerSend.
#     """
#     to_list = [{"email": to_email}]
#     if to_name:
#         to_list[0]["name"] = to_name

#     email = (
#         EmailBuilder()
#         .from_email("anaahemedshehta@test-r9084zv96kegw63d.mlsender.net", "NGD System")
#         .to_many(to_list)
#         .subject(subject)
#         .html(body)
#         .text("This is an HTML email. Please enable HTML to view it.")
#         .build()
#     )
#     response = ms.emails.send(email)
#     if response.status_code != 202:
#         print(f"[MailerSend Error] Status: {response.status_code}, Response: {response.text}")
#     else:print("The Email without Attachment Send Sucessfully !")      


# def send_email_with_attachment(
#     subject: str, body: str, to_email: str, attachment_path: str, to_name: Optional[str] = None
# ):
#     """
#     Send an email with attachment via MailerSend.
#     """
#     to_list = [{"email": to_email}]
#     if to_name:
#         to_list[0]["name"] = to_name

#     email = (
#         EmailBuilder()
#         .from_email("anaahmedshehta@test-r9084zv96kegw63d.mlsender.net", "NGD System")
#         .to_many(to_list)
#         .subject(subject)
#         .html(body)
#         .text("This is an HTML email. Please enable HTML to view it.")
#         .attach_file(attachment_path)  # MailerSend supports attaching files by path
#         .build()
#     )
#     response = ms.emails.send(email)
#     if response.status_code != 202:
#         print(f"[MailerSend Error] Status: {response.status_code}, Response: {response.text}")
        
#     print("The Email with Attachment Send Sucessfully !")    


# # ---- Background wrappers for FastAPI ----

# def send_request_email(request_number: str, category: str, user_email: str, first_name:str , background_tasks: BackgroundTasks):
#     """
#     Send confirmation email to user when they submit a request.
#     """
#     subject = f"NGD - Your {category} request has been received"
#     body = f"""
#     <p>Dear {first_name},</p>
#     <p>We have received your <strong>{category}</strong> request with number <strong>{request_number}</strong>.</p>
#     <p>Our team will review it and respond as soon as possible.</p>
#     <p>Thank you for your submission.</p>
#     """
#     background_tasks.add_task(send_email, subject, body, user_email)
#     print("The Email of Request Send Sucessfully !")


# def send_reply_email(request_number: str, user_email: str, reply_body: str, background_tasks: BackgroundTasks):
#     """
#     Send reply email to user after admin responds.
#     """
#     subject = f"NGD - Response to your request {request_number}"
#     body = f"""
#     <p>Dear user,</p>
#     <p>We have responded to your request <strong>{request_number}</strong>:</p>
#     <p>{reply_body}</p>
#     <p>Thank you for using our system.</p>
#     """
#     background_tasks.add_task(send_email, subject, body, user_email)
    
#     print("The Email for Replay to Request Sucessfully !")


