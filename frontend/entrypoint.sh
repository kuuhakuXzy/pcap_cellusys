#!/bin/sh
envsubst < /usr/share/nginx/html/config.template.js > /usr/share/nginx/html/config.js

envsubst '80' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

#Start NGINX
exec "$@"