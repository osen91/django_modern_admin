from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings

# The scope for the OAuth2 request.
SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'


# The location of the key file with the key data.
KEY_FILEPATH = settings.GOOGLE_ANALYTICS_SERVICE_ACCOUNT_JSON


# Cache the credentials object
__credentials = None


# Gets the credentials object from the cache if available,
# otherwise generates it from the key file.
def get_credentials():
  global __credentials

  if __credentials:
    return __credentials
  else:
    # Constructs a credentials objects from the key file and OAuth2 scope.
    __credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILEPATH, SCOPE)

    return __credentials


# Defines a method to get an access token from the credentials object.
# The access token is automatically refreshed if it has expired.
def get_access_token():
  return get_credentials().get_access_token().access_token