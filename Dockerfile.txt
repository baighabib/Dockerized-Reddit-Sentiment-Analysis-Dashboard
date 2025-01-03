# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements and source files
COPY requirements.txt .
COPY api.py .
COPY transform.py .
COPY load.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit's default port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "load.py", "--server.port=8501", "--server.enableCORS=false"]
