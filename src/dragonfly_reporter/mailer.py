"""Sending emails."""

from logging import getLogger

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

from dragonfly_reporter.constants import Mail

logger = getLogger(__name__)


async def send_mail(
    graph_client: GraphServiceClient,
    to_addresses: list[str],
    bcc_addresses: list[str],
    subject: str,
    content: str,
    attachments: list[Attachment] | None = None,
) -> None:
    """Send an email."""
    sender = EmailAddress(address=Mail.sender)

    from_recipient = Recipient(email_address=sender)

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
        from_escaped=from_recipient,
        to_recipients=to_recipients,
        bcc_recipients=bcc_recipients,
        body=email_body,
    )
    if attachments is not None:
        message.attachments = attachments

    request_body = SendMailPostRequestBody()
    request_body.message = message
    await graph_client.users.by_user_id(Mail.sender).send_mail.post(request_body)
