import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class MailerService:
    def __init__(self):
        self.sender_email = "ugliar.arsen@gmail.com"
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")

    async def send(self, recipient_email: str, subject: str, content: str) -> str:
        message = Mail(
            from_email=self.sender_email,
            to_emails=recipient_email,
            subject=subject,
            plain_text_content=content
        )

        try:
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)

            if response.status_code == 202:
                msg = f"Email sent successfully to {recipient_email}!\nSubject: {subject}.\nContent: {content}."
                print(msg)

                return [True, msg]
            else:
                raise Exception(f"Failed to send email: {response.body}")
        except Exception as e:
            print(f"Failed to send email: {e}")
            return [False, f"Failed to send email: {e}"]
