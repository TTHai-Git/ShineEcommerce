FROM python:3.12
ENV PYTHONUNBUFFERED 1
WORKDIR /ecosmetics
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy toàn bộ mã nguồn vào container
COPY . .

## Tạo migrations và áp dụng chúng
RUN python manage.py makemigrations
RUN python manage.py migrate

#CMD  python manage.py runserver 0.0.0.0:8000
# Expose the Django production server port
EXPOSE 8000
# Lệnh mặc định để chạy server Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
