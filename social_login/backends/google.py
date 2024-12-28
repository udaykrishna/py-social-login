import logging
from typing import Optional, Union, Iterable, List
from .oauth_models import OAuthInfo, OAuthToken, OAuth2Manager
from pydantic import BaseModel
import jwt
import json
from jwt.algorithms import Algorithm


class GoogleOAuthToken(OAuthToken):
    azp: Union[str, None] = None
    email: Union[str, None] = None
    email_verified: bool = False
    at_hash: Union[str, None] = None
    name: Union[str, None] = None
    picture: Union[str, None] = None
    given_name: Union[str, None] = None
    family_name: Union[str, None] = None
    locale: Union[str, None] = None
    hd: Optional[str] = None

    class Config:
        extra = 'allow'

    @classmethod
    def create(cls, data):
        data['email_verified'] = (data.get('email_verified', "false") == "true")
        return cls(**data)


class GoogleOAuthInfo(OAuthInfo):
    provider: str = 'google'
    name: Union[str, None] = None
    email: Union[str, None] = None
    access_token: Union[str, None] = None
    picture: Union[str, None] = None
    given_name: Union[str, None] = None
    family_name: Union[str, None] = None
    token: GoogleOAuthToken
    valid_iss: List = ['accounts.google.com', 'https://accounts.google.com']
    valid_hd: List = []
    
    def is_valid_hd(self):
        """
        valid host domain to lock domain to for example udaykrishna.com
        """
        if (len(self.valid_hd)>0):
            return (self.token.hd in self.valid_hd)
        return True
    
    def validate(self):
        return super().validate() and self.is_valid_hd()
    
    def _update_info_from_token(self):
        self.oauth_id = self.token.sub
        self.name = self.token.name
        self.email = self.token.email
        self.access_token = self.token.access_token
        self.picture = self.token.picture
        self.given_name = self.token.given_name
        self.family_name = self.token.family_name


class GoogleOAuth2Manager(OAuth2Manager):
    name = 'google-oauth2'
    TOKEN_CLASS = GoogleOAuthToken
    USERINFO_CLASS = GoogleOAuthInfo
    REDIRECT_STATE = False
    REVOKE_TOKEN_URL = 'https://accounts.google.com/o/oauth2/revoke'
    REVOKE_TOKEN_METHOD = 'GET'
    VERIFY_TOKEN_URL = 'https://oauth2.googleapis.com/tokeninfo'
    VERIFY_TOKEN_METHOD = 'GET'
    CERTS_URL = 'https://www.googleapis.com/oauth2/v3/certs'
    CERTS_METHOD = 'GET'
    CERTS = {}

    def fetch_tokeninfo(self, token):
        url = self.VERIFY_TOKEN_URL+'?id_token={token}'.format(token=token)
        data = self.get_json(self.VERIFY_TOKEN_METHOD, url)
        return data

    def get_user_data(self, login_data, valid_aud=[], valid_hd=[], ignore_aud=False, user_info_overrides={}):
        valid_aud.append(self.client_id)
        if login_data.get('id_token'):
            jwt_token = login_data["id_token"]
            token_data = self.parse_token(jwt_token, valid_aud=valid_aud, ignore_aud=ignore_aud)
            login_data.update(token_data)
        token = self.TOKEN_CLASS(**login_data)
        user_info_overrides.update({"valid_aud":valid_aud, "valid_hd":valid_hd})
        userInfo = self.USERINFO_CLASS.from_token(token, overrides=user_info_overrides)
        return userInfo