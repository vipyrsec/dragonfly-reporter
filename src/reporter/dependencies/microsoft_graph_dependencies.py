"""Microsoft Graph integration."""

from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient

from reporter.constants import Microsoft


def build_graph_client() -> GraphServiceClient:
    """Build authenticated GraphClient."""
    credential = ClientSecretCredential(
        tenant_id=Microsoft.tenant_id,
        client_id=Microsoft.client_id,
        client_secret=Microsoft.client_secret,
    )
    return GraphServiceClient(credentials=credential, scopes=Microsoft.scopes)
