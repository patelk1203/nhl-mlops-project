# 1. Start with a lightweight official Python image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install the requests library for our API calls
RUN pip install requests

# 4. Copy our ingestion script from the Codespace into the container
COPY ingest.py /app/

# 5. Define the default command to run when the container starts
CMD ["python", "ingest.py"]
