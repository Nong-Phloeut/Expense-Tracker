# Use official nginx image
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY default.conf /etc/nginx/conf.d/

# Copy Django static files from volume (optional)
# This is only needed if you mount Django's static files here
# COPY --from=app /app/static /usr/share/nginx/html/static
