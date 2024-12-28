from flask import Flask, render_template, request
from backends.google import GoogleOAuth2Manager
from backends.apple import AppleOAuth2Manager
from backends.constants import GOOG_CLIENT_ID, SOCIAL_AUTH_APPLE_KEY_ID, SOCIAL_AUTH_APPLE_TEAM_ID, SOCIAL_AUTH_APPLE_PRIVATE_KEY, APPLE_CLIENT_ID, SOCIAL_AUTH_APPLE_AUD
import json

app = Flask(__name__)
ga = GoogleOAuth2Manager(GOOG_CLIENT_ID)
apple = AppleOAuth2Manager(APPLE_CLIENT_ID)

@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/login', methods = ['POST'])
def login():
    data = json.loads(request.data)
    resp = ga.get_user_data(data["data"])
    print(resp)
    print("----------")
    print(resp.is_valid)
    print("----------")
    return resp.dict()

@app.route('/login-google', methods = ['GET'])
def test():
    return render_template('google.html', GOOG_CLIENT_ID=GOOG_CLIENT_ID)

@app.route('/apple-login', methods = ['GET'])
def apple_login():
    # test tokens expired
    data = {'access_token': 'a5cc72b7bda2e4cf9ad_51ef66f07ca2d6.0.mrtuq.cOqqA_YzEiegB2mtq07GlQ', 'token_type': 'Bearer', 'expires_in': 3600, 'refresh_token': 'raee624756e7b4ab2b0787f45b14b1ac7.0.mrtuq.9mtptaAy788v2L8zAKLH9w', 'id_token': 'eyJraWQiOiI4NkQ4OEtmIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJodHRwczovL2FwcGxlaWQuYXBwbGUuY29tIiwiYXVkIjoiY29tLnRvcHByLkludGVybmF0aW9uYWxEb3VidHMiLCJleHAiOjE1ODkyNzUzMDMsImlhdCI6MTU4OTI3NDcwMywic3ViIjoiMDAxMzQwLjk1ZDk4MmNkNzM5NjQyZWVhNTg2ODE1Yjk1ZjI0NDcwLjExMzAiLCJub25jZSI6IjFlYmE4NzU3MzlkODA2YmE3MmI3Mjc0ODM0MzlmNDI4YjA5YmEyM2VhOTQwMjVjMWFkNTVjYTM4NjI0YWFmNmMiLCJhdF9oYXNoIjoickRTa3cwVXM4d1JzRjI3SmE1TWJSUSIsImVtYWlsIjoiNnA5cmpqZWZlbkBwcml2YXRlcmVsYXkuYXBwbGVpZC5jb20iLCJlbWFpbF92ZXJpZmllZCI6InRydWUiLCJpc19wcml2YXRlX2VtYWlsIjoidHJ1ZSIsImF1dGhfdGltZSI6MTU4OTI3NDYxNiwibm9uY2Vfc3VwcG9ydGVkIjp0cnVlfQ.ErX9C1hW4c4gssIU8z0jAUDaXi0_2f-VGXgmKRa-Yk2F9oY0I5OPjM1apMQTu0TqcEUbpbdyLlxctnrLgTV2B-1qyGKjQF1JdwRjv-mJZVnxyvjmLKi0A9lU2nQdbvSn8ZWgXbWTZ0X2OePpZOAjt_wGjW_bQM5LjU05ya4Zd10mp0KizOnuIb1tZkMDpY-21y5bsz7DG_mi0I295mPGw6_WhBD5iZz7LjNh24MnPTgSPp71rTKal8ZVowoVseQXAMbdayN3ph0OvEA4MW3U6SuNLVcAbZpkJ84YSiUQvaUHBbZ-RmGzvGTWTEcc-4Lt_fSBX8ImSb3SHlrtpplbPQ'}
    auth_code = 'c5fed798fa2a249b58449d9569d20af56.0.nrtuq.nDzWzKLXe-Fes3mxzKPGuA'
    resp = apple.get_user_data(data)
    print(resp.is_valid)
    return resp.dict()


@app.route('/google')
def google():
    return render_template('google.html', GOOG_CLIENT_ID=GOOG_CLIENT_ID)

@app.route('/facebook')
def facebook():
    return render_template('facebook.html', GOOG_CLIENT_ID=GOOG_CLIENT_ID)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)