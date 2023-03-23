FROM python@sha256:93fb93c461a2e47a2176706fad1f39eaacd5dd40e19c0b018699a28c03eb2e2a

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
ADD ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

ADD . /app

# Expose port
EXPOSE 8000

# Run app.py when the container launches
CMD ["gunicorn", "--bind", ":8000", "--log-level", "debug", "main:app"]
