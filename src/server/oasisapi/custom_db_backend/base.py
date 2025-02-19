from django.db.backends.postgresql.base import DatabaseWrapper as PostgresDatabaseBase
from django.core.exceptions import ImproperlyConfigured

from ....conf import iniconf


# ---- Example class to fake fetchting a token ----
""" This should be replaced with "from azure.identity import ClientSecretCredential"
"""
class FakeClientSecretCredential:
    def __init__(self, tenant_id, client_id, client_secret, fake_token_return="oasis"):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.fake_return = fake_token_return

    def get_token(self, scope):
        return self.fake_return

# ------------------------------------------------


class DatabaseWrapper(PostgresDatabaseBase):
    vendor = "custom_postgresql"
    display_name = "CustomPostgreSQL"
    scope = iniconf.settings.get('server', 'AZURE_CLIENT_SCOPE', fallback='https://ossrdbms-aad.database.windows.net/.default')
    credential = FakeClientSecretCredential(
        tenant_id=iniconf.settings.get('server','AZURE_TENANT_ID', fallback=None),
        client_id=iniconf.settings.get('server','AZURE_CLIENT_ID', fallback=None),
        client_secret=iniconf.settings.get('server','AZURE_CLIENT_SECRET', fallback=None)
    )

    def _generate_token(self):
        try:
            return self.credential.get_token(self.scope)
        except Exception as e:
            raise ImproperlyConfigured(f"Failed to retrieve access token: {e}")

    def get_new_connection(self, conn_params):
        """Add token to connection parameters"""
        conn_params['password'] = self._generate_token()
        return super().get_new_connection(conn_params)
