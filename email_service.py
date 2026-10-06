from __future__ import annotations
import os, smtplib, ssl
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()

class EmailService:
    def __init__(self):
        self.host=os.getenv("SMTP_HOST",""); self.port=int(os.getenv("SMTP_PORT","587"))
        self.username=os.getenv("SMTP_USERNAME",""); self.password=os.getenv("SMTP_PASSWORD","")
        self.sender=os.getenv("SMTP_FROM",self.username); self.use_tls=os.getenv("SMTP_USE_TLS","true").lower()=="true"
    @property
    def configured(self): return bool(self.host and self.username and self.password and self.sender)
    def send(self,to_email,subject,body):
        if not self.configured: raise RuntimeError("Email is not configured. Add SMTP settings to .env.")
        msg=EmailMessage(); msg["Subject"]=subject; msg["From"]=self.sender; msg["To"]=to_email; msg.set_content(body)
        with smtplib.SMTP(self.host,self.port,timeout=20) as smtp:
            if self.use_tls: smtp.starttls(context=ssl.create_default_context())
            smtp.login(self.username,self.password); smtp.send_message(msg)
