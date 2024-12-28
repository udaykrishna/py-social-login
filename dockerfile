from atlassian/pipelines-awscli
WORKDIR sociallogin/

RUN apk add --no-cache --virtual .build-deps g++ python3-dev libffi-dev openssl-dev && \
    apk add --no-cache --update python3 && \
    pip3 install --upgrade pip setuptools && \
    pip3 install wheel

COPY . .


RUN python3 setup.py sdist bdist_wheel 

# ENTRYPOINT ['/bin/bash']

CMD '/bin/bash'