FROM nginx:alpine

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create HSAP directory structure
RUN mkdir -p /var/www/hsap/attestations

# Copy default files (will be overwritten by volume mount)
COPY manifest.json /var/www/hsap/
COPY pubkey.pem /var/www/hsap/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
