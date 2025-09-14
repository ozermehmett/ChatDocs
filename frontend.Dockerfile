FROM nginx:alpine

COPY src/frontend/ /usr/share/nginx/html/

COPY frontend-nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]