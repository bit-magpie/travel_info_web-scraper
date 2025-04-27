# Use Python 3.10 image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy your application code
COPY ./app/ /app/

# Install dependencies and the travel_app package
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install -e .

# Set the default command to run your app
CMD ["python", "-m", "travel_app.main"]
