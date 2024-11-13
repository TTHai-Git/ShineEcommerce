from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from rest_framework.exceptions import ValidationError


# Enum classes
class RoleEnum(models.TextChoices):
    ADMIN = 'Quản trị viên'
    STAFF = 'Nhân viên'
    CUSTOMER = 'Khách hàng'


class PaymentEnum(models.TextChoices):
    COD = 'Thanh toán khi nhận hàng'
    ATM = 'Thanh toán bằng thẻ ATM nội địa'
    INTERNET_BANKING = 'Chuyển khoản'
    VISA_MASTER = 'Thanh toán thẻ Visa/MasterCard'


class ShipmentEnum(models.TextChoices):
    ON_SITE = 'Nhận tại cửa hàng'
    DELIVERY = 'Giao hàng tận nơi'


# class NotificationEnum(models.TextChoices):
#     NOTIFICATION = 'Thông báo'
#     EVENT = 'Sự kiện'
#     BLOG = 'Blog'


class Role(models.Model):
    name = models.CharField(max_length=50, choices=RoleEnum.choices, primary_key=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    name = models.CharField(max_length=50, choices=PaymentEnum.choices, primary_key=True)

    def __str__(self):
        return self.name


class Shipment(models.Model):
    name = models.CharField(max_length=50, choices=ShipmentEnum.choices, primary_key=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    def validate_mail(value):
        if not value.endswith("@gmail.com") and not value.endswith("@ou.edu.vn"):
            raise ValidationError("Phải dùng tài khoản Gmail (@gmail.com)")

    dob = models.DateField(null=True)
    address = models.CharField(max_length=254, null=True)
    phone = models.CharField(max_length=10, null=True)
    email = models.EmailField(validators=[validate_mail], unique=True)
    avatar = CloudinaryField('avatar', null=True, blank=True,
                             default="https://res.cloudinary.com/dh5jcbzly/image/upload""/v1718648320"
                                     "/r77u5n3w3ddyy4yqqamp.jpg")
    sex = models.BooleanField(null=True, default=False)
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    def __str__(self):
        return f'{self.id} - {self.last_name} {self.first_name} - {self.username} - {self.role}'


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.id} - {self.name}'


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.id} - {self.name}'


class Origin(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.id} - {self.name}'


class Product(BaseModel):
    name = models.CharField(max_length=255)
    # unit_price = models.DecimalField(max_digits=20, decimal_places=3)
    unit_price = models.FloatField()
    color = models.CharField(max_length=100, null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    image = CloudinaryField('image', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='products', null=True, blank=True)
    origins = models.ManyToManyField(Origin, related_name='products', null=True, blank=True)
    discount = models.IntegerField(default=0, null=True)

    def clean(self):
        if not (0 <= self.discount <= 100):
            raise ValidationError("Percent must be between 0 and 100.")
        if not (0 <= self.unit_price <= 1000000000.0):
            raise ValidationError("Unit price must be between 0 and 1000000.0")

    def __str__(self):
        return f'{self.id} - {self.name} - {self.category.name} - {self.discount}'


class PromotionTicket(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    min_order_value = models.FloatField(default=0, null=True)
    expiry_date = models.DateTimeField(null=True)
    expiry_number_used = models.IntegerField(default=0)
    discount_price = models.FloatField(default=0, null=True)


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderDetail', related_name='orders')
    city = models.CharField(max_length=100, null=True)
    district = models.CharField(max_length=50, null=True)
    ward = models.CharField(max_length=50, null=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    payment_type = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    shipment_type = models.ForeignKey(
        Shipment, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    shipment_address = models.CharField(max_length=255, null=True, blank=True)
    temp_total_amount = models.FloatField(default=0, null=True)
    vat_price = models.FloatField(default=0, null=True)
    shipping_fee = models.FloatField(default=0, null=True)
    total_amount = models.FloatField(default=0, null=True)
    is_payment = models.BooleanField(default=False)
    promotion_ticket = models.ForeignKey(PromotionTicket, default=None, null=True, on_delete=models.CASCADE)

    def clean(self):
        # Ensure that total_amount is within an acceptable range
        if not 0 <= self.total_amount:
            raise ValidationError("Total amount must be > 0")

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'


class OrderDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_amount = models.FloatField(default=0, null=True)
    discount_price = models.FloatField(default=0, null=True)

    def clean(self):
        # Ensure that quantity is positive
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        # Ensure that total_amount is within an acceptable range
        if not (0 <= self.total_amount <= 1000000.0):
            raise ValidationError("Total amount must be between 0 and 1,000,000.")

    def __str__(self):
        return f'OrderDetail: {self.product.name} (x{self.quantity})'


class Interaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Comment(Interaction):
    content = models.TextField()
    star = models.IntegerField(null=True, default=0)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.product.name}'


# class Like(Interaction):
#     class Meta:
#         unique_together = ('user', 'product')
#
#     def __str__(self):
#         return f'Like by {self.user.username} on {self.product.name}'

class Blog(BaseModel):
    title = models.CharField(max_length=100, null=True, default=None)
    description = models.CharField(max_length=100, null=True, default=None)
    content = RichTextField()
    image = CloudinaryField('image', null=True, blank=True)
    # type = models.CharField(max_length=50, choices=NotificationEnum.choices, null=True)


class Contact(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    title = models.CharField(max_length=100)
    content = RichTextField()

    def __str__(self):
        return f'Contact from {self.user.username}: {self.title}'
