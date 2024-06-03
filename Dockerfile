# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first, for leveraging Docker layer caching
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable for Redis connection string
ENV REDIS_CONN_STRING=redis://host.docker.internal:6379

# Run streamlit when the container launches
CMD ["streamlit", "run", "chat.py"]