#!/bin/bash

#export FLASK_DEBUG=0
export FLASK_APP='app.py'

FLASK_PORT=443

META_SERVER='169.254.169.254'
PUBLIC_IP=$(curl --connect-timeout 5 http:///$META_SERVER/latest/meta-data/public-ipv4)
PUBLIC_IP="${PUBLIC_IP:-127.0.0.1}"

echo public ip is "${PUBLIC_IP}"

openssl genrsa -out webhook_pkey.pem 2048
openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem \
        -subj /C=RU/ST=MOSCOW/L=0/O=Dis/CN=$PUBLIC_IP

export PUBLIC_IP=${PUBLIC_IP} # use source ./<name>.sh to run bash-script in current shell-env

flask main initdb
#flask main create_fake_data
flask main set_me_as_admin
flask run -p $FLASK_PORT --host 0.0.0.0 --cert webhook_cert.pem --key webhook_pkey.pem