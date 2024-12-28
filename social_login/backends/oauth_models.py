from pydantic import BaseModel
from typing import List, Union
import requests
import json
import logging
import time
import jwt

class OAuthToken(BaseModel):
    iss: Union[str, None] = None
    sub: Union[str, None] = None
    exp: Union[int, None] = 0
    aud: Union[str, None] = None
    iat: Union[int, None] = None
    jti: Union[str, None] = None
    alg: Union[str, None] = None
    kid: Union[str, None] = None
    typ: Union[str, None] = 'JWT'
    claim_valid: bool = False
    access_token: str = ''
    
    class Config:
        extra = 'allow'

    def __post_init__(self):
        self.exp = float(self.exp)
    
    @property
    def expires_at(self):
        return self.exp

    @classmethod
    def create(cls, data):
        return cls(**data)


class OAuthInfo(BaseModel):
    provider: Union[str, None] = 'base'
    oauth_id: Union[str, None] = None
    token: OAuthToken
    valid_aud:List = []
    valid_iss:List = []
    ID_KEY: str = 'sub'

    class Config:
        extra = 'allow'
        arbitrary_types_allowed = True

    def is_valid_iss(self):
        return self.token.iss in self.valid_iss
    
    def is_valid_aud(self):
        if (len(self.valid_aud)>0):
            return (self.token.aud in self.valid_aud)
        return True

    def is_expired(self):
        return self.token.exp < time.time()

    @property
    def is_valid(self):
        return self.validate()

    def validate(self):
        return self.token.claim_valid and self.is_valid_iss() and self.is_valid_aud() and (not self.is_expired())
    
    def _update_info_from_token(self):
        self.oauth_id = self.token.dict()[self.ID_KEY]
    
    @classmethod
    def from_token(cls, oauthToken, overrides={}):
        data = {"token": oauthToken,
                         "valid_aud": overrides["valid_aud"]}
        data.update(overrides)
        oAuthInfo = cls(**data)
        oAuthInfo._update_info_from_token()
        oAuthInfo.is_valid
        return oAuthInfo
        



class OAuth2Manager(object):
    name = 'base-oauth2'
    TOKEN_CLASS = OAuthToken
    USERINFO_CLASS = OAuthInfo
    REDIRECT_STATE = False
    REVOKE_TOKEN_URL = None
    REVOKE_TOKEN_METHOD = None
    VERIFY_TOKEN_URL = None
    VERIFY_TOKEN_METHOD = None
    CERTS_METHOD = 'GET'
    CERTS_URL=''
    CERTS = {}

    def __init__(self, client_id, client_secret=''):
        self.client_id = client_id
        self.client_secret = client_secret
        if len(self.CERTS_URL)>0:
            self.refresh_certs()

    @classmethod
    def request(self, method, url, *args, **kwargs):
        return requests.request(method, url, *args, **kwargs)

    @classmethod
    def get_json(self, method, url, *args, **kwargs):
        resp = self.request(method, url, *args, **kwargs)
        if resp.ok:
            if resp.content is None:
                return {}
            else:
                return json.loads(resp.content.decode())
        else:
            logging.error("invalid response + {}".format(resp.content))
    
    def refresh_certs(self):
        certs_jwk_list = self.get_json(self.CERTS_METHOD, self.CERTS_URL).get('keys', [])
        self.CERTS = {jwk['kid']:self.get_cert_from_jwk(jwk) for jwk in certs_jwk_list}
    
    def get_cert_from_jwk(self, jwk):
        algos = jwt.algorithms.get_default_algorithms()
        alg = jwk['alg']
        cert = algos[alg].from_jwk(json.dumps(jwk))
        return cert
    
    def get_cert(self, kid, _try=0, _max_refreshes=2):
        try:
            cert = self.CERTS[kid]
            return cert
        except KeyError:
            if _try<_max_refreshes:
                self.refresh_certs()
                return self.get_cert(kid, _try=_try+1)
            else:
                return None
    
    def parse_token(self, jwt_token, valid_aud=[], ignore_aud=False):
        
        unverified_data = jwt.decode(jwt_token, '', verify=False, options={'verify_signature': False})
        if ignore_aud:
            valid_aud.append(unverified_data.get('aud'))
        headers = jwt.get_unverified_header(jwt_token)
        data_overides = {"alg":headers.get("alg"), "kid":headers.get("kid")}
        try:
            decoded_data = jwt.decode(jwt_token, self.get_cert(headers['kid']), audience=valid_aud, verify=True)
            decoded_data["claim_valid"] = True
            data = decoded_data
        except jwt.exceptions.InvalidTokenError as e:
            unverified_data["claim_valid"] = False
            data = unverified_data
            data.error_reason = e.__repr__()
        finally:
            data.update(data_overides)
            return data
    
    def get_user_data(self, login_data, valid_aud=[], ignore_aud=False, user_info_overrides={}):
        valid_aud.append(self.client_id)
        if login_data.get('id_token'):
            token_data = self.parse_token(login_data['id_token'], valid_aud=valid_aud, ignore_aud=ignore_aud)
            login_data.update(token_data)
        token = self.TOKEN_CLASS(**login_data)
        user_info_overrides.update({"valid_aud":valid_aud})
        userInfo = self.USERINFO_CLASS.from_token(token, overrides=user_info_overrides)
        return userInfo
        
