# Use Python 3.10 image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy your application code
COPY ./app/requirements.txt /app/.

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set the default command to run your app
CMD ["python", "-m", "app.main"]
