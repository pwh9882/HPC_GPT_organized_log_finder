import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from credentials import email, password  # 이메일과 비밀번호를 불러옵니다.

def send_reset_email(receiver_email):
    sender_email = email  # 발신자 이메일 주소

    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"""\
    Hi,
    Click the link below to reset your password:
    http://example.com/reset-password?email={receiver_email}
    """
    html = f"""\
    <html>
      <body>
        <p>Hi,<br>
           Click the link below to reset your password:<br>
           <a href="http://example.com/reset-password?email={receiver_email}">Reset Password</a>
        </p>
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return False

# SMTP 설정 테스트 함수 추가
def test_smtp():
    sender_email = email
    receiver_email = "hwooo22@naver.com"  # 테스트 수신자 이메일 주소
    test_password = password

    message = MIMEMultipart("alternative")
    message["Subject"] = "Test Email"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = "This is a test email."
    part1 = MIMEText(text, "plain")
    message.attach(part1)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, test_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")

# 이 파일을 직접 실행할 때만 테스트 함수를 호출합니다.
if __name__ == "__main__":
    test_smtp()
