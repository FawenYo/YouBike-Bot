FROM python@sha256:d811538656b665bba649b3ac2c3fc8a5187e24cd510a34d7e905d7ec4534fb89

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
