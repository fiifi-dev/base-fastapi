import logging
from pathlib import Path
from typing import Any

import emails
from emails.template import JinjaTemplate
from app.core import models

from app.core.config import settings


def get_template_str(template_filename: str):
    template_path = f"{settings.EMAIL_TEMPLATES_DIR}/{template_filename}"

    with open(template_path) as f:
        template_str = f.read()

    return template_str


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: dict[str, Any] = {},
) -> None:
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}

    if settings.SMTP_TLS:
        smtp_options["tls"] = True

    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER

    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    response = message.send(to=email_to, render=environment, smtp=smtp_options)

    logging.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"

    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=get_template_str("test_email.html"),
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(user: models.User, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {user.email}"

    link = f"{settings.SERVER_HOST}/{user.id}/reset-password?token={token}"

    send_email(
        email_to=user.email,
        subject_template=subject,
        html_template=get_template_str("reset_password.html"),
        environment={
            "project_name": settings.PROJECT_NAME,
            "email": user.email,
            "link": link,
        },
    )


def send_new_account_email(user: models.User, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"Complete Your Registration for {project_name}"
    link = f"{settings.SERVER_HOST}/{user.id}/activate-account?token={token}"

    send_email(
        email_to=user.email,
        subject_template=subject,
        html_template=get_template_str("new_account.html"),
        environment={
            "project_name": settings.PROJECT_NAME,
            "email": user.email,
            "link": link,
        },
    )
