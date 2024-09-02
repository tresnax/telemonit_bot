FROM python:3.8-slim

# Change workdir
WORKDIR /app

# Copy Apps
COPY . .

# Install dependency
RUN pip install --no-cache-dir -r requirements.txt

# Create databases
RUN python createdb.py

# Run apps
CMD [ "python", "app.py" ]