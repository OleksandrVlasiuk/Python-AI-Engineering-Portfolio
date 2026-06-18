import smtplib
from email.mime.text import MIMEText
from auth import utils
from config.config import EMAIL_ADDRESS, EMAIL_PASSWORD, FRONTEND_URL



def send_mail(email: str):
    token = utils.create_verification_token(email)

    letter_content = f"Subject: Verify email\n\n {FRONTEND_URL}verification?token={token}"
    receiver = [email]
    receiver = ", ".join(receiver)

    msg = MIMEText(letter_content)
    msg['Subject'] = "Verification"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = receiver

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp_server.sendmail(EMAIL_ADDRESS, receiver, msg.as_string())

    print(f"Message sent sent to {receiver}")

