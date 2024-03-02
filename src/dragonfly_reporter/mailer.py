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
    sender = EmailAddress()
    sender.address = Mail.sender

    from_recipient = Recipient()
    from_recipient.email_address = sender

    to_recipients = []
    for to_address in to_addresses:
        recipient_email = EmailAddress()
        recipient_email.address = to_address

        to_recipient = Recipient()
        to_recipient.email_address = recipient_email
        to_recipients.append(to_recipient)  # pyright: ignore [reportUnknownMemberType]

    bcc_recipients = []
    for bcc_address in bcc_addresses:
        recipient_email = EmailAddress()
        recipient_email.address = bcc_address

        to_recipient = Recipient()
        to_recipient.email_address = recipient_email
        bcc_recipients.append(to_recipient)  # pyright: ignore [reportUnknownMemberType]

    email_body = ItemBody()
    email_body.content = content
    email_body.content_type = BodyType.Html

    message = Message()
    message.subject = subject
    message.from_escaped = from_recipient
    message.to_recipients = to_recipients
    message.bcc_recipients = bcc_recipients
    message.body = email_body
    if attachments is not None:
        message.attachments = attachments

    request_body = SendMailPostRequestBody()
    request_body.message = message
    await graph_client.users.by_user_id(Mail.sender).send_mail.post(request_body)
