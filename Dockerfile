FROM python:3.11.8-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN pip install --no-cache-dir --no-deps --index-url https://download.pytorch.org/whl/cpu torch==2.2.2+cpu torchvision==0.17.2+cpu \
    && pip install --no-cache-dir --no-deps mirtorch==0.1.2 torchkbnufft==1.4
COPY . /workspace
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--ServerApp.token=", "--ServerApp.password="]
