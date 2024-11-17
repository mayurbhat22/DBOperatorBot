FROM python:3.11-slim
WORKDIR /app

ARG DBUSER
ARG DBPASS
ARG DBHOST
ARG DBPORT
ARG DBSCHEMA
ARG OPENAI_API_KEY

# Set environment variables
ENV DBUSER=${DBUSER}
ENV DBPASS=${DBPASS}
ENV DBHOST=${DBHOST}
ENV DBPORT=${DBPORT}
ENV DBSCHEMA=${DBSCHEMA}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# Copy the current directory contents into the container at /app
COPY . ./

# Install any necessary dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install -r requirements.txt

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]