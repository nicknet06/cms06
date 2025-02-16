FROM alpine:latest

# Install Python, pip, nginx, and MySQL client
RUN apk add --no-cache python3 py3-pip nginx mysql-client mariadb-connector-c-dev build-base python3-dev

# Create app directory
WORKDIR /app

# Create virtual environment and activate it
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Copy nginx configuration
COPY nginx.conf /etc/nginx/http.d/default.conf

# Create necessary directories for nginx
RUN mkdir -p /run/nginx

# Expose port 80
EXPOSE 80

# Start nginx and the Flask app
CMD ["sh", "-c", "nginx && python3 app.py"]