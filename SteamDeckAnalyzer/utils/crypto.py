# -*- coding: utf-8 -*-

import urllib
from array import array
from javax.crypto import Cipher, SecretKeyFactory
from javax.crypto.spec import PBEKeySpec, IvParameterSpec, SecretKeySpec


class CryptoUtils:

    @staticmethod
    def decrypt_chrome_secrets_linux_v10(ciphertext, 
                         password=b"peanuts", salt=b"saltysalt", iv=b" "*16, 
                         key_len=16, iterations=1, prettify=True):
        # adapted from: https://stackoverflow.com/a/23727331
        # historical note: https://chromium.googlesource.com/chromium/src/+/53.0.2785.100/components/os_crypt/os_crypt_linux.cc#35

        assert isinstance(ciphertext, str) or isinstance(ciphertext, list) \
            or isinstance(ciphertext, array), "{} >> {}".format(type(ciphertext), ciphertext)

        if isinstance(ciphertext, array):
            ciphertext = list(ciphertext)
        if isinstance(ciphertext, list):
            ciphertext = ''.join(map(lambda x: chr(x % 256), ciphertext))

        # derive decryption key from password, salt, number of iterations, and key length
        decryption_key = CryptoUtils.__pbkdf2_sha1(password, salt, iterations, key_len)

        # check and remove prefix from ciphertext; only v10 supported (hardcoded decryption key)
        assert ciphertext.startswith(b'v10'), "{}".format(ciphertext)
        ciphertext = ciphertext[3:]

        # decrypting the ciphertext using derived decryption key and initialization vector
        plaintext = CryptoUtils.__decrypt_aes_cbc(ciphertext, decryption_key, iv)

        if prettify:
            try:
                # unquote URL-encoded JSON payload
                _ = urllib.unquote(plaintext)
                plaintext = _
            except:
                pass

        return plaintext

    @staticmethod
    def __pbkdf2_sha1(password, salt, iterations, key_length):
        key_spec = PBEKeySpec(password, salt, iterations, key_length * 8)
        key_factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1")
        key = key_factory.generateSecret(key_spec)
        return key.getEncoded()

    @staticmethod
    def __decrypt_aes_cbc(ciphertext, key, iv):
        cipher = Cipher.getInstance("AES/CBC/NoPadding")
        spec_key = SecretKeySpec(key, "AES")
        spec_iv = IvParameterSpec(iv)
        cipher.init(Cipher.DECRYPT_MODE, spec_key, spec_iv)
        plaintext = cipher.doFinal(ciphertext)
        plaintext = ''.join(map(lambda x: chr(x % 256), plaintext))
        plaintext = plaintext[:-ord(plaintext[-1])]  # rm padding
        plaintext = plaintext.strip()
        return plaintext
