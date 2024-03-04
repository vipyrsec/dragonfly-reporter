"""Sending emails."""

from logging import getLogger
from typing import Optional

from msgraph import GraphServiceClient
from msgraph.generated.models.attachment import Attachment
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody,
)
from textwrap import dedent
from reporter.constants import Mail
from reporter.utils.pypi import file_path_from_inspector_url

logger = getLogger(__name__)

def build_report_email_content(
    *,
    name: str,
    version: str,
    inspector_url: str,
    rules_matched: list[str],
    additional_information: Optional[str],
) -> str:
    content = f"""
        PyPI Malicious Package Report
        -
        Package Name: {name}
        Version: {version}
        File path: {file_path_from_inspector_url(inspector_url)}
        Inspector URL: {inspector_url}
        Additional Information: {additional_information or "No user description provided"}
        Yara rules matched: {", ".join(rules_matched) or "No rules matched"}
    """

    return dedent(content)


async def send_mail(
    graph_client: GraphServiceClient,
    to_addresses: list[str],
    bcc_addresses: list[str],
    subject: str,
    content: str,
    attachments: list[Attachment] | None = None,
) -> None:
    """Send an email."""
    reply_to_recipient = Recipient(email_address=EmailAddress(address=Mail.reply_to))
    from_recipient = Recipient(email_address=EmailAddress(address=Mail.sender))

    to_recipients = [
        Recipient(email_address=EmailAddress(address=to_address))
        for to_address in to_addresses
    ]

    bcc_recipients = [
        Recipient(email_address=EmailAddress(address=bcc_address))
        for bcc_address in bcc_addresses
    ]

    email_body = ItemBody(content=content, content_type=BodyType.Html)

    message = Message(
        subject=subject,
        reply_to=[reply_to_recipient],
        from_=from_recipient,
        to_recipients=to_recipients,
        bcc_recipients=bcc_recipients,
        body=email_body,
    )
    if attachments is not None:
        message.attachments = attachments

    request_body = SendMailPostRequestBody(message=message)
    await graph_client.users.by_user_id(Mail.sender).send_mail.post(request_body)
