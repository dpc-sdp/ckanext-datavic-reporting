# encoding: utf-8

import logging
import mimetypes
import os
import smtplib
import socket
from email import encoders, utils
from email.header import Header
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import time

import ckan
import ckan.common
from ckan.common import _, config
from ckan.lib.base import render

log = logging.getLogger(__name__)


class MailerException(Exception):
    pass


def _mail_recipient(
    recipient_name,
    recipient_email,
    sender_name,
    sender_url,
    subject,
    body,
    body_html=None,
    headers=None,
    attachments=[],
):

    if not headers:
        headers = {}

    mail_from = config.get("smtp.mail_from")
    reply_to = config.get("smtp.reply_to")
    if body_html:
        # multipart
        msg = MIMEMultipart("alternative")
        part1 = MIMEText(body.encode("utf-8"), "plain", "utf-8")
        part2 = MIMEText(body_html.encode("utf-8"), "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)
    else:
        # just plain text
        msg = MIMEMultipart("alternative")
        part1 = MIMEText(body.encode("utf-8"), "plain", "utf-8")
        msg.attach(part1)
    for k, v in headers.items():
        if k in msg.keys():
            msg.replace_header(k, v)
        else:
            msg.add_header(k, v)
    if attachments:
        _add_attachments(msg, attachments)
    subject = Header(subject.encode("utf-8"), "utf-8")
    msg["Subject"] = subject
    msg["From"] = _("%s <%s>") % (sender_name, mail_from)
    recipient = "%s <%s>" % (recipient_name, recipient_email)
    msg["To"] = Header(recipient, "utf-8")
    msg["Date"] = utils.formatdate(time())
    msg["X-Mailer"] = "CKAN %s" % ckan.__version__
    if reply_to and reply_to != "":
        msg["Reply-to"] = reply_to

    # Send the email using Python's smtplib.
    smtp_connection = smtplib.SMTP()
    if "smtp.test_server" in config:
        # If 'smtp.test_server' is configured we assume we're running tests,
        # and don't use the smtp.server, starttls, user, password etc. options.
        smtp_server = config["smtp.test_server"]
        smtp_starttls = False
        smtp_user = None
        smtp_password = None
    else:
        smtp_server = config.get("smtp.server", "localhost")
        smtp_starttls = ckan.common.asbool(config.get("smtp.starttls"))
        smtp_user = config.get("smtp.user")
        smtp_password = config.get("smtp.password")

    try:
        smtp_connection.connect(smtp_server)
    except socket.error as e:
        log.exception(e)
        raise MailerException(
            'SMTP server could not be connected to: "%s" %s' % (smtp_server, e)
        )
    try:
        # Identify ourselves and prompt the server for supported features.
        smtp_connection.ehlo()

        # If 'smtp.starttls' is on in CKAN config, try to put the SMTP
        # connection into TLS mode.
        if smtp_starttls:
            if smtp_connection.has_extn("STARTTLS"):
                smtp_connection.starttls()
                # Re-identify ourselves over TLS connection.
                smtp_connection.ehlo()
            else:
                raise MailerException("SMTP server does not support STARTTLS")

        # If 'smtp.user' is in CKAN config, try to login to SMTP server.
        if smtp_user:
            assert smtp_password, (
                "If smtp.user is configured then "
                "smtp.password must be configured as well."
            )
            smtp_connection.login(smtp_user, smtp_password)

        smtp_connection.sendmail(mail_from, [recipient_email], msg.as_string())
        log.info("Sent email to {0}".format(recipient_email))

    except smtplib.SMTPException as e:
        msg = "%r" % e
        log.exception(msg)
        raise MailerException(msg)
    finally:
        smtp_connection.quit()


def _add_attachments(msg, attachments):
    """Adds attachments to email"""
    for path in attachments:
        filename = os.path.basename(path)
        ctype, encoding = mimetypes.guess_type(filename)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split("/", 1)
        if maintype == "text":
            fp = open(path)
            # Note: we should handle calculating the charset
            attachment = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "image":
            fp = open(path, "rb")
            attachment = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "audio":
            fp = open(path, "rb")
            attachment = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(path, "rb")
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)

        attachment.add_header(
            "Content-Disposition", "attachment", filename=filename
        )
        msg.attach(attachment)


def mail_recipient(
    recipient_name,
    recipient_email,
    subject,
    body,
    body_html=None,
    headers={},
    attachments=[],
):
    """Sends an email"""
    site_title = config.get("ckan.site_title")
    site_url = config.get("ckan.site_url")
    return _mail_recipient(
        recipient_name,
        recipient_email,
        site_title,
        site_url,
        subject,
        body,
        body_html=body_html,
        headers=headers,
        attachments=attachments,
    )


def mail_user(
    recipient, subject, body, body_html=None, headers={}, attachments=[]
):
    """Sends an email to a CKAN user"""
    if (recipient.email is None) or not len(recipient.email):
        raise MailerException(_("No recipient email address available!"))
    mail_recipient(
        recipient.display_name,
        recipient.email,
        subject,
        body,
        body_html=body_html,
        headers=headers,
        attachments=attachments,
    )


def send_scheduled_report_email(user_emails, email_type, extra_vars):
    if not user_emails or len(user_emails) == 0:
        return
    subject = render("emails/subjects/{0}.txt".format(email_type), extra_vars)
    body = render("emails/bodies/{0}.txt".format(email_type), extra_vars)
    attachments = [extra_vars.get("file_path")]
    log.debug("Attempting to send {0} to: {1}".format(email_type, user_emails))
    for user_email in user_emails:
        try:
            # Attempt to send mail.
            mail_dict = {
                "recipient_name": user_email,
                "recipient_email": user_email,
                "subject": subject,
                "body": body,
                "attachments": attachments,
            }
            mail_recipient(**mail_dict)
        except (MailerException, socket.error):
            log.error(
                "Failed to send scheduled report email to %s.",
                user_email,
                exc_info=1,
            )
