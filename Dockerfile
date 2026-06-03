# Task 4: Write a cache-friendly Dockerfile.
#
# Requirements (in order):
# 1. Use python:3.11-slim as the base image.
# 2. Copy requirements.txt BEFORE copying source code.
# 3. Install dependencies from requirements.txt.
# 4. Copy src/ into the image.
# 5. Set the CMD to run the pipeline: python -m src.pipeline
#
# Replace each TODO comment with the correct Dockerfile instruction.

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY data/ data/

CMD ["python", "-m", "src.pipeline"]
