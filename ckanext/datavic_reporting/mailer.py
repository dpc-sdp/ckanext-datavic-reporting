# encoding: utf-8
"""Email functionality for datavic-reporting extension.

This module provides email sending for scheduled reports, using the core
CKAN mailer for the actual email delivery.
"""
from __future__ import annotations

import logging
import os

import ckan.plugins.toolkit as tk

log = logging.getLogger(__name__)


def send_scheduled_report_email(
    user_emails: list[str],
    email_type: str,
    extra_vars: dict,
) -> None:
    """Send scheduled report emails with file attachment.

    Args:
        user_emails: List of email addresses to send to.
        email_type: The email template type (e.g., 'scheduled_report').
        extra_vars: Template variables including 'file_path' for attachment.
    """
    if not user_emails:
        return

    subject = tk.render(f"emails/subjects/{email_type}.txt", extra_vars)
    body = tk.render(f"emails/bodies/{email_type}.txt", extra_vars)
    file_path = extra_vars.get("file_path")

    log.debug("Attempting to send %s to: %s", email_type, user_emails)

    for user_email in user_emails:
        try:
            if file_path and os.path.exists(file_path):
                # Open file and create attachment tuple (name, file_object)
                # The file must remain open during mail_recipient call
                with open(file_path, "rb") as f:
                    attachments = [(os.path.basename(file_path), f)]
                    tk.mail_recipient(
                        recipient_name=user_email,
                        recipient_email=user_email,
                        subject=subject,
                        body=body,
                        attachments=attachments,
                    )
            else:
                # Send without attachment if no file
                tk.mail_recipient(
                    recipient_name=user_email,
                    recipient_email=user_email,
                    subject=subject,
                    body=body,
                )
        except Exception:
            log.error(
                "Failed to send scheduled report email to %s.",
                user_email,
                exc_info=True,
            )
