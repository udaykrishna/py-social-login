import jwt
import time
import logging
from typing import Union, List
from .oauth_models import OAuthInfo, OAuthToken, OAuth2Manager
from pydantic import BaseModel
import json
from jwt.algorithms import Algorithm


class AppleOAuthToken(OAuthToken):
    auth_time: str = None
    email: str = None
    email_verified: str = None
    is_private_email: str = None
    nonce: str = None
    nonce_supported: str = None
    refresh_token: str = None

    class Config:
        extra = 'allow'

    @classmethod
    def create(cls, data):
        return cls(**data)


class AppleOAuthInfo(OAuthInfo):
    provider: str = 'apple'
    email: Union[str, None] = None
    token: AppleOAuthToken
    valid_iss: List = ['https://appleid.apple.com']
    # ID_KEY = 'uid'

    def _update_info_from_token(self):
        self.email = self.token.email
        self.email_verified = self.token.email_verified
        self.is_private_email = self.token.is_private_email
        super()._update_info_from_token()


class AppleOAuth2Manager(OAuth2Manager):
    """apple authentication backend"""
    name = 'apple-oauth2'
    TOKEN_CLASS = AppleOAuthToken
    USERINFO_CLASS = AppleOAuthInfo
    REDIRECT_STATE = False
    CERTS_URL = 'https://appleid.apple.com/auth/keys'
    CERTS_METHOD = 'GET'
    ACCESS_TOKEN_URL = 'https://appleid.apple.com/auth/token'
    ACCESS_TOKEN_METHOD = 'POST'
    CERTS = {}
    SCOPE_SEPARATOR = ','
    
    def __init__(self, client_id=None, private_key=None, key_id=None, team_id=None, client_secret=''):
        self.client_id = client_id
        self.key_id = key_id
        self.team_id = team_id
        self.private_key = private_key
        self.client_secret = client_secret
        super().__init__(self.client_id, self.client_secret)

    def do_auth(self, access_token, *args, **kwargs):
        """
        Finish the auth process once the access_token was retrieved
        Get the email from ID token received from apple
        """
        self.update_secret()
        # return {'access_token': 'ae6166982a5664bed8667dc63b3c5b354.0.mrtuq.8mqFTjMvHAws85B6sscS2A', 'token_type': 'Bearer', 'expires_in': 3600, 'refresh_token': 'r4618a4768bab4ac3abfbdedf59cb0dbd.0.mrtuq.8DPB7r4kLx2ZMYD1p3Clgg', 'id_token': 'eyJraWQiOiI4NkQ4OEtmIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJodHRwczovL2FwcGxlaWQuYXBwbGUuY29tIiwiYXVkIjoiY29tLnRvcHByLkludGVybmF0aW9uYWxEb3VidHMiLCJleHAiOjE1ODkzMDc5NjUsImlhdCI6MTU4OTMwNzM2NSwic3ViIjoiMDAxMzQwLjk1ZDk4MmNkNzM5NjQyZWVhNTg2ODE1Yjk1ZjI0NDcwLjExMzAiLCJub25jZSI6IjBlNjI0MTU0NjM5YTE5YWEyZDRkOGQ3OWFlNmEyZDRkNjEzNDliMDMzMWIyMTNjMjMzM2I3ZDQ0ZTllOGQ5MTkiLCJhdF9oYXNoIjoiUU95NlRNOWNtSmxmQm8xa3VYQUI5dyIsImVtYWlsIjoiNnA5cmpqZWZlbkBwcml2YXRlcmVsYXkuYXBwbGVpZC5jb20iLCJlbWFpbF92ZXJpZmllZCI6InRydWUiLCJpc19wcml2YXRlX2VtYWlsIjoidHJ1ZSIsImF1dGhfdGltZSI6MTU4OTMwNzA3Miwibm9uY2Vfc3VwcG9ydGVkIjp0cnVlfQ.RTif6F6fAj8DqCGGN5spQnQ2HjzkG8qzMdIN8uuETI9c9Avfct2tqXgAi4n0hAy5dGReaI_uHWXhlPJqeed9wzCQLyHBB_SI-OJKDS1HnD-vJ2-esyobIOGy6GE465HQKM9BtdcmXxX9x2AJmQ9bnp1cRa5IcJ-MucFrarY5o5nIa89jEaS4LPiA__Z4_htyRIPyhq-cRHtVGxrYPSAdcC9c_KFCF4Gkp8f2mqgOZclNuBCclabhTotmcMMUeRaNYF-CvzX23qGEYFtjFudW3DFfuAXW6MjWWJwQczE3NbXRvWAB2L92MvnryobX-SkxzwzeSKyBX-isypQub3T-Fg'}
        headers = {'content-type': "application/x-www-form-urlencoded"}
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': access_token,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://udaykrishna.com'
        }

        res = self.get_json(self.ACCESS_TOKEN_METHOD, self.ACCESS_TOKEN_URL, data=data, headers=headers)
        return res

    def update_secret(self):
        self.secret = self.get_secret()
    
    def get_secret(self):
        headers = {
            'kid': self.key_id
        }
        now = int(time.time())
        payload = {
            'iss': self.team_id,
            'iat': now,
            'exp': now + (6 * 30 * 24 * 60 * 60),
            'aud': 'https://appleid.apple.com',
            'sub': self.client_id,
        }
        client_secret = jwt.encode(
            payload, 
            self.private_key,
            algorithm='ES256', 
            headers=headers
        ).decode("utf-8")
        
        return client_secret
