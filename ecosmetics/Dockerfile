FROM python:3.12
ENV PYTHONUNBUFFERED 1
WORKDIR /ecosmetics
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy toàn bộ mã nguồn vào container
COPY . .
# Lệnh mặc định để chạy server Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
