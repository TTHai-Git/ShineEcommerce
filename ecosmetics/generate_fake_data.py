import os

import django
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from oauth2_provider.models import Application
from cosmetics.models import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          './ecosmetics/settings.py')  # Replace 'my_project.settings' with your settings module
django.setup()


class Command(BaseCommand):
    help = 'Generate fake data for models'

    def handle(self, *args, **kwargs):
        self.clean_database()
        self.create_roles()  # Ensure roles exist before creating users
        self.create_payment()
        self.create_shipment()
        self.create_superuser()
        self.create_oauth_application()
        self.generate_category()
        self.generate_tag()
        self.generate_orgigin()
        self.generate_blog()
        self.generate_product()
        self.generate_PromotionTicket()

    def create_roles(self):
        # Ensure roles exist in the system
        for role_name in RoleEnum.choices:
            Role.objects.get_or_create(name=role_name[0])

    def create_payment(self):
        # Ensure roles exist in the system
        for payment_name in PaymentEnum.choices:
            Payment.objects.get_or_create(name=payment_name[0])

    def create_shipment(self):
        # Ensure roles exist in the system
        for shipment_name in ShipmentEnum.choices:
            Shipment.objects.get_or_create(name=shipment_name[0])

    def create_superuser(self):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            superuser = User.objects.create_superuser(
                username='admin',
                email='admin@ou.edu.vn',
                password='admin',  # No need to hash the password here, Django handles that in `create_superuser`
                role=Role.objects.get(name="Quản trị viên")
            )
            superuser.save()

    def create_oauth_application(self):
        if not Application.objects.filter(user__username='admin').exists():
            superuser = get_user_model().objects.get(username='admin')
            Application.objects.create(
                user=superuser,
                client_id=os.getenv('client_id_db_oauth_toolkit'),
                client_secret=os.getenv('client_secret_db_oauth_toolkit'),
                client_type='confidential',
                authorization_grant_type='password'
            )

    def generate_category(self):
        Category.objects.create(name="SẢN PHẨM CHĂM SÓC DA")
        Category.objects.create(name="SẢN PHẨM CHĂM SÓC TÓC")
        Category.objects.create(name="SẢN PHẨM CHĂM SÓC BODY")

    def generate_tag(self):
        Tag.objects.create(name="KHUYẾN MÃI MỖI NGÀY")
        Tag.objects.create(name="SẢN PHẨM TỐT NHẤT")

    def generate_orgigin(self):
        Origin.objects.create(name="Việt Nam")
        Origin.objects.create(name="Hàn Quốc")
        Origin.objects.create(name="Nhật Bản")
        Origin.objects.create(name="Thái Lan")
        Origin.objects.create(name="Ý")
        Origin.objects.create(name="Mỹ")
        Origin.objects.create(name="Nga")
        Origin.objects.create(name="Tất Cả")

    def generate_blog(self):
        Blog.objects.create(title="Blog số 1", description='Mô tả blog số 1', content='Nội dung blog số 1',
                            image='https://res.cloudinary.com/dh5jcbzly/image/upload/v1730524416/dp5bukj32omreggikbin'
                                  '.png')
        Blog.objects.create(title="Blog số 2", description='Mô tả blog số 2', content='Nội dung blog số 2',
                            image='https://res.cloudinary.com/dh5jcbzly/image/upload/v1730524416/dp5bukj32omreggikbin'
                                  '.png')
        Blog.objects.create(title="Blog số 3", description='Mô tả blog số 2', content='Nội dung blog số 3',
                            image='https://res.cloudinary.com/dh5jcbzly/image/upload/v1730524416/dp5bukj32omreggikbin'
                                  '.png')
        Blog.objects.create(title="Blog số 4", description='Mô tả blog số 2', content='Nội dung blog số 4',
                            image='https://res.cloudinary.com/dh5jcbzly/image/upload/v1730524416/dp5bukj32omreggikbin'
                                  '.png')
        Blog.objects.create(title="Blog số 5", description='Mô tả blog số 2', content='Nội dung blog số 5',
                            image='https://res.cloudinary.com/dh5jcbzly/image/upload/v1730524416/dp5bukj32omreggikbin'
                                  '.png')
        Blog.objects.create(title="Blog số 6", description='Mô tả blog số 6', content='Nội dung blog số 6',
                            image='https://res.cloudinary.com/dh5jcbzly/image/upload/v1730524416/dp5bukj32omreggikbin'
                                  '.png')

    def generate_product(self):
        Product.objects.create(name='Bộ Kem Trị Nám Giori Nhật Bản', unit_price=2222000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 1',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729404870"
                                     "/dmpeimrvqfgtfkblwuy6.png",
                               category=Category.objects.get(id=1), tags=Tag.objects.get(id=1),
                               origins=Origin.objects.get(id=1), discount=10)
        Product.objects.create(name='Son Shu Uemura chính hãng Nhật Bản', unit_price=4690000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 2',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729404984"
                                     "/g2sfh9bzty2jw7gynzrj.png",
                               category=Category.objects.get(id=2), tags=Tag.objects.get(id=2),
                               origins=Origin.objects.get(id=2), discount=20)
        Product.objects.create(name='Bộ Kem Trị Nám Giori', unit_price=7770000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 3',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729404870"
                                     "/dmpeimrvqfgtfkblwuy6.png",
                               category=Category.objects.get(id=3), tags=Tag.objects.get(id=2),
                               origins=Origin.objects.get(id=3), discount=5)
        Product.objects.create(name='Hình Nộm Người Mẫu', unit_price=9990000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 4',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729575801"
                                     "/friczfd9z8qdksoszlu6.jpg",
                               category=Category.objects.get(id=3), tags=Tag.objects.get(id=1),
                               origins=Origin.objects.get(id=2), discount=10)
        Product.objects.create(name='Bộ Kem Trị Nám Giori Nhật Bản', unit_price=2222000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 1',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729404870"
                                     "/dmpeimrvqfgtfkblwuy6.png",
                               category=Category.objects.get(id=1), tags=Tag.objects.get(id=1),
                               origins=Origin.objects.get(id=1), discount=10)
        Product.objects.create(name='Son Shu Uemura chính hãng Nhật Bản', unit_price=4690000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 2',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729404984"
                                     "/g2sfh9bzty2jw7gynzrj.png",
                               category=Category.objects.get(id=2), tags=Tag.objects.get(id=2),
                               origins=Origin.objects.get(id=2), discount=20)
        Product.objects.create(name='Bộ Kem Trị Nám Giori', unit_price=7770000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 3',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729404870"
                                     "/dmpeimrvqfgtfkblwuy6.png",
                               category=Category.objects.get(id=3), tags=Tag.objects.get(id=2),
                               origins=Origin.objects.get(id=3), discount=5)
        Product.objects.create(name='Hình Nộm Người Mẫu', unit_price=9990000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 4',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729575801"
                                     "/friczfd9z8qdksoszlu6.jpg",
                               category=Category.objects.get(id=3), tags=Tag.objects.get(id=1),
                               origins=Origin.objects.get(id=2), discount=10)
        Product.objects.create(name='Bộ Kem Trị Nám Giori Nhật Bản', unit_price=2222000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 1',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729404870"
                                     "/dmpeimrvqfgtfkblwuy6.png",
                               category=Category.objects.get(id=1), tags=Tag.objects.get(id=1),
                               origins=Origin.objects.get(id=1), discount=10)
        Product.objects.create(name='Son Shu Uemura chính hãng Nhật Bản', unit_price=4690000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 2',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729404984"
                                     "/g2sfh9bzty2jw7gynzrj.png",
                               category=Category.objects.get(id=2), tags=Tag.objects.get(id=2),
                               origins=Origin.objects.get(id=2), discount=20)
        Product.objects.create(name='Bộ Kem Trị Nám Giori', unit_price=7770000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 3',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729404870"
                                     "/dmpeimrvqfgtfkblwuy6.png",
                               category=Category.objects.get(id=3), tags=Tag.objects.get(id=2),
                               origins=Origin.objects.get(id=3), discount=5)
        Product.objects.create(name='Hình Nộm Người Mẫu', unit_price=9990000,
                               color='#e08271 - #000 - #b3b3b3', description='mô tả sp 4',
                               iamge="https://res.cloudinary.com/dh5jcbzly/image/upload/v1729575801"
                                     "/friczfd9z8qdksoszlu6.jpg",
                               category=Category.objects.get(id=3), tags=Tag.objects.get(id=1),
                               origins=Origin.objects.get(id=2), discount=10)

    def generate_PromotionTicket(self):
        PromotionTicket.ojects.create(code='abc123', min_order_value=1111111, expiry_date='2024-12-31 23:59:59.000000',
                                      expiry_number_used=100, discount_price=500000)
        PromotionTicket.ojects.create(code='xyz123', min_order_value=1111111, expiry_date='2024-12-31 23:59:59.000000',
                                      expiry_number_used=100, discount_price=500000)
        PromotionTicket.ojects.create(code='abc456', min_order_value=1111111, expiry_date='2024-12-31 23:59:59.000000',
                                      expiry_number_used=100, discount_price=500000)
        PromotionTicket.ojects.create(code='xyz789', min_order_value=1111111, expiry_date='2024-12-31 23:59:59.000000',
                                      expiry_number_used=100, discount_price=500000)
        PromotionTicket.ojects.create(code='abc222', min_order_value=1111111, expiry_date='2024-12-31 23:59:59.000000',
                                      expiry_number_used=100, discount_price=500000)
        PromotionTicket.ojects.create(code='xyz222', min_order_value=1111111, expiry_date='2024-12-31 23:59:59.000000',
                                      expiry_number_used=100, discount_price=500000)

    def generate_comment(self):
        Comment.objects.create(content="Comment số 1", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=1))
        Comment.objects.create(content="Comment số 2", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=1))
        Comment.objects.create(content="Comment số 3", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=1))

        Comment.objects.create(content="Comment số 1", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=2))
        Comment.objects.create(content="Comment số 2", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=2))
        Comment.objects.create(content="Comment số 3", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=2))

        Comment.objects.create(content="Comment số 1", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=3))
        Comment.objects.create(content="Comment số 2", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=3))
        Comment.objects.create(content="Comment số 3", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=3))

        Comment.objects.create(content="Comment số 1", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=4))
        Comment.objects.create(content="Comment số 2", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=4))
        Comment.objects.create(content="Comment số 3", star=5,
                               user=User.objects.get(id=1), product=Product.objects.get(id=4))