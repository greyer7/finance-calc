from email.message import EmailMessage

import aiosmtplib
from jinja2 import Environment, BaseLoader

from app.config import settings

# --- Простий inline-шаблон листа (Jinja2). 
VERIFICATION_EMAIL_TEMPLATE = """
<html>
  <body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2>Підтвердження email</h2>
    <p>Дякуємо за реєстрацію у Finance Calculator!</p>
    <p>Щоб підтвердити свою email-адресу, перейдіть за посиланням нижче:</p>
    <p>
      <a href="{{ verification_link }}"
         style="background-color: #4CAF50; color: white; padding: 10px 20px;
                text-decoration: none; border-radius: 5px;">
        Підтвердити email
      </a>
    </p>
    <p>Або скопіюйте це посилання в браузер:</p>
    <p>{{ verification_link }}</p>
    <p style="color: #888; font-size: 12px;">
      Посилання дійсне протягом 24 годин. Якщо ви не реєструвались — просто проігноруйте цей лист.
    </p>
  </body>
</html>
"""

jinja_env = Environment(loader=BaseLoader())


async def send_verification_email(to_email: str, verification_token: str) -> None:
    verification_link = f"{settings.frontend_url}/verify-email?token={verification_token}"

    template = jinja_env.from_string(VERIFICATION_EMAIL_TEMPLATE)
    html_content = template.render(verification_link=verification_link)

    message = EmailMessage()
    message["From"] = settings.smtp_user
    message["To"] = to_email
    message["Subject"] = "Підтвердіть вашу email-адресу — Finance Calculator"
    message.set_content("Щоб підтвердити email, використовуйте HTML-версію цього листа.")
    message.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        start_tls=True,
    )