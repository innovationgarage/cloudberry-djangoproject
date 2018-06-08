import django.contrib.auth.hashers
import hashlib
import base64
import django.utils.encoding
import collections
from django.utils.translation import gettext_noop as _

class FreeradiusSHA1PasswordHasher(django.contrib.auth.hashers.BasePasswordHasher):
    """
    Based on django.contrib.auth.hashers.SHA1PasswordHasher but modified to make hashes convertible to the format Freeradius
    uses for the User-Password attribute.

    To convert to Freeradius-format, remove the $ separating algorithm and hash, and surround the algorithm name with { and }.

    Differences from django.contrib.auth.hashers.SHA1PasswordHasher:

    * Hashed value is password+salt instead of salt+password
    * Hash and salt (in that order) are stored together with no separator
    * Hash and salt are base64-encoded instead of salt being unencoded and hash being hex-coded
    """
    algorithm = "radiussha1"

    def encode(self, password, salt):
        assert password is not None
        assert salt and '$' not in salt
        
        return "%s$%s" % (
            self.algorithm,
            base64.b64encode(
                hashlib.sha1(
                    password.encode('utf-8') + salt.encode('utf-8')
                ).digest()
                + salt.encode('utf-8')).decode("utf-8"))

    def verify(self, password, encoded):
        algorithm, hash = encoded.split('$', 1)
        assert algorithm == self.algorithm

        salt = base64.b64decode(hash)[20:].decode('utf-8')
        encoded_2 = self.encode(password, salt)

        print("%s == %s" % (encoded, encoded_2))
        return django.contrib.auth.hashers.constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, hash = encoded.split('$', 1)
        assert algorithm == self.algorithm

        salt = hash[29:]
        hash = hash[:29]

        return collections.OrderedDict([
            (_('algorithm'), algorithm),
            (_('salt'), django.contrib.auth.hashers.mask_hash(salt, show=2)),
            (_('hash'), django.contrib.auth.hashers.mask_hash(hash)),
        ])

    def harden_runtime(self, password, encoded):
        pass
