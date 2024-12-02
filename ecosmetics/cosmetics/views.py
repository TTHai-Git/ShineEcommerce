from datetime import datetime, timedelta
import cloudinary
import jwt
from cloudinary.uploader import destroy
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils import timezone
from jwt import ExpiredSignatureError, InvalidTokenError
from rest_framework import viewsets, generics, parsers, status, permissions
from cosmetics import serializers, paginators
from cosmetics.models import *
from django.db.models import F
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

# Create your views here.
from ecosmetics import settings


def index(request):
    return HttpResponse("ScoreApp")


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_permissions(self):
        if self.action in ['current_user']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get', 'patch'], detail=False, url_path='current-user', url_name='current-user')
    def current_user(self, request):
        user = request.user
        try:
            if request.method == 'PATCH':
                for k, v in request.data.items():
                    if k == 'password':
                        user.set_password(v)
                    elif k == 'avatar':
                        new_avatar = cloudinary.uploader.upload(request.data['avatar'])
                        user.avatar = new_avatar['secure_url']
                    elif k == 'sex':
                        if v == "false":
                            setattr(user, k, False)
                        else:
                            setattr(user, k, True)
                    else:
                        if k != "role" and k != "access_token" and k != "sex":
                            setattr(user, k, v)
                user.save()
                return Response({'message': 'Cập nhật thông tin cá nhân thành công'}, status=status.HTTP_200_OK)
            else:
                return Response(serializers.UserSerializer(user).data)
        except Exception as ex:
            return Response({"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=False, url_path='cart/payment', parser_classes=[parsers.JSONParser],
            url_name='cart/payment')
    def payment(self, request):
        try:
            order = request.data.get('order')
            order_details = request.data.get('order_details')
            if order['termsAccepted']:
                if order:
                    # Create the main order
                    new_order = Order.objects.create(
                        user_id=(order['user_id']),
                        city=order['city'],
                        district=order['district'],
                        ward=order['ward'],
                        note=order['note'],
                        payment_type=Payment.objects.get(name=order['payment_type']),
                        shipment_type=Shipment.objects.get(name=order['shipment_type']),
                        shipment_address=order['shipment_address'],
                        temp_total_amount=float(order['temp_total_amount']),
                        vat_price=float(order['vat_price']),
                        shipping_fee=float(order['shipping_fee']),
                        total_amount=float(order['total_amount']),
                    )
                    if order['promotion_ticket_code'] != "":
                        new_order.promotion_ticket = PromotionTicket.objects.get(code=order['promotion_ticket_code'])

                    if order['payment_type'] == "Thanh toán khi nhận hàng":
                        new_order.is_payment = False
                    else:
                        new_order.is_payment = True

                    new_order.save()
                    # Create each order detail
                    for order_detail in order_details:
                        OrderDetail.objects.create(
                            product_id=order_detail['id_product'],
                            order=new_order,
                            quantity=order_detail['quantity'],
                            discount_price=float(order_detail['discount_price']),
                            total_amount=float(order_detail['total_amount'])
                        )

                    return Response({"message": "Tạo Hoá Đơn Đặt Hàng Và Thanh Toán Thành Công"},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Khách hàng vui lòng chấp thuận điều khoản trước khi đặt hàng! "},
                                status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @action(methods=['post'], url_path='contact/send-mail-support', detail=True)
    # def send_mail_support(self, request, pk=None):
    #     user = self.get_object()
    #     descriptions = request.query_params.get('descriptions')
    #     subject = request.query_params.get('subject')
    #
    #     subject = f"{subject}"
    #     message = f"\nHọ và tên người dùng: {user.last_name} {user.first_name} " \
    #               f"\nEmail: {user.email}" \
    #               f"\nSố điện thoại: {user.phone}" \
    #               f"\nNội dung: {descriptions}" \
    #
    #     from_email = user.email
    #     email_message = EmailMessage(
    #         subject,
    #         message,
    #         from_email,
    #         [settings.EMAIL_HOST_USER]
    #     )
    #     email_message.send()
    #     return Response({'message': f'ĐÃ GỬI EMAIL HỖ TRỢ TỚI HỆ THỐNG. '
    #                                 f'ADMIN SẼ REPLY LẠI QUA MAIL BẠN TRONG VÒNG 1 TUẦN'},
    #                     status=status.HTTP_201_CREATED)
    @action(methods=['get'], url_path='orders', detail=True)
    def show_orders(self, request, pk=None):
        try:
            data = []

            user = self.get_object()
            orders = Order.objects.filter(user=user, is_payment=True)

            # Map order status to user-friendly labels
            status_mapping = {
                "NEW": "Chờ xác nhận",
                "CONFIRMED": "Đã xác nhận",
                "PROCESSING": "Đang xử lý",
                "SHIPPING": "Đang giao hàng",
                "DELIVERED": "Đã giao hàng",
                "CANCELLED": "Đã hủy",
                "RETURNED": "Hoàn trả",
                "REFUNDED": "Hoàn tiền",
                "FAILED": "Thất bại",
            }

            if orders.exists():
                for order in orders:
                    data.append({
                        "order_id": order.id,
                        "order_created_date": order.created_date,
                        "order_total_amount": order.total_amount,
                        "order_shipping_fee": order.shipping_fee,
                        "order_payment_type": order.payment_type.name if order.payment_type else None,
                        "order_shipment_type": order.shipment_type.name if order.shipment_type else None,
                        "order_shipment_address": order.shipment_address,
                        "order_is_payment": order.is_payment,
                        "order_note": order.note,
                        "order_status": status_mapping.get(order.status, order.status),  # Use mapped status
                        "order_updated_date": order.updated_date,
                    })

                # Paginate data

                paginator = paginators.OrdersOfCustomerPaginator()
                page = paginator.paginate_queryset(data, request)
                return paginator.get_paginated_response(page)
            else:
                return Response({"message": "Không có đơn hàng nào!!!"}, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get', 'post'], url_path='send-otp', parser_classes=[parsers.JSONParser], detail=False)
    def send_otp(self, request):
        username = request.data.get('username')
        user = User.objects.get(username=username)
        try:
            if user:
                # Thời gian token hết hạn là sau 10 phút
                valid_until = timezone.now() + timedelta(minutes=10)
                # kẹp username và expire time của token vào payload của token
                token_payload = {
                    "username": user.username,
                    "exp": valid_until.timestamp()
                }
                token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')  # Mã hóa token

                subject = 'Mail Reset Password website ShineEcommerce'
                message = f'Mã Otp reset password của bạn dùng trong 1 lần ' \
                          f'hết hạn trong vòng 10 phút kể từ lúc gửi mail: {token}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email]
                send_mail(subject, message, email_from, recipient_list, fail_silently=False)
                return Response({'message': f'ĐÃ GỬI TOKEN RESET PASSWORD TỚI EMAIL: {user.email} CỦA BẠN.'},
                                status=status.HTTP_200_OK)
            return Response({'message': f'GỬI TOKEN RESET PASSWORD THẤT BẠI! NGƯỜI DÙNG KHÔNG TỒN TẠI.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"message": str(ex)}
                            , status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['patch'], detail=False, url_path='change-password', parser_classes=[parsers.JSONParser])
    def change_password(self, request):
        new_password = request.data.get('new_password')
        token = request.data.get('token')

        try:
            # Giải mã token từ token mã hóa gửi qua email thông qua payload của token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            # Lấy username từ payload của token kẹp vào
            username = payload.get('username')
            user = User.objects.filter(username=username).first()

            if not user:
                return Response({'message': 'Email không tồn tại.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'message': 'Đặt lại mật khẩu thành công.'}, status=status.HTTP_200_OK)
        except ExpiredSignatureError:
            return Response({'message': 'Token đã hết hạn.'}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidTokenError:
            return Response({'message': 'Token không hợp lệ.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OriginsViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView,
                     generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Origin.objects.all()
    serializer_class = serializers.OriginSerializer
    pagination_class = paginators.OriginPaginator


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView,
                      generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    pagination_class = paginators.CategoryPaginator

    @action(methods=['GET'], url_path='list-product', detail=True)
    def load_list_product(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(category=category)

        # Extract query parameters
        try:
            max_price = float(request.query_params.get('max_price')) if request.query_params.get('max_price') else None
            min_price = float(request.query_params.get('min_price')) if request.query_params.get('min_price') else None
        except ValueError:
            raise ValidationError("Invalid min_price or max_price value.")

        origin = request.query_params.get('origin') if request.query_params.get('origin') else None
        sort_order = request.query_params.get('sort_order') if request.query_params.get('sort_order') else None

        # Filter products by origin if provided
        if origin and origin != "Tất Cả":
            products = products.filter(origins__name=origin)

        # Calculate present price and filter by min_price/max_price if provided
        products = products.annotate(
            present_price=F('unit_price') - (F('unit_price') * F('discount') / 100)
        )

        if min_price is not None and max_price is not None:
            products = products.filter(present_price__gte=min_price, present_price__lte=max_price)
        elif min_price is not None:
            products = products.filter(present_price__gte=min_price)
        elif max_price is not None:
            products = products.filter(present_price__lte=max_price)

        if sort_order == 'asc':
            products = products.order_by('present_price')
        elif sort_order == 'desc':
            products = products.order_by('-present_price')
        elif sort_order == 'new':
            products = products.order_by('-id')

        # Prepare response data
        results = [
            {
                "id_product": product.id,
                "image_product": product.image,
                "name_product": product.name,
                "name_category": product.category.name,
                "unit_price_product": product.unit_price,
                "discount_product": product.discount,
                "present_price": product.present_price,
            }
            for product in products
        ]

        # Handle pagination
        paginator = paginators.ProductOfCategoryPaginator()
        page = paginator.paginate_queryset(results, request)
        serializer = serializers.RelatedProductSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView,
                 generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = paginators.TagPaginator


class CommentViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    pagination_class = paginators.CommentPaginator

    @action(methods=['delete'], url_path='del-comment', detail=True)
    def del_comment(self, request, pk=None):
        comment = self.get_object()
        comment_files = comment.files.all()
        user = request.user
        try:
            if comment.user == user:
                if comment_files:
                    for comment_file in comment_files:
                        result = destroy(comment_file.file_public_id,
                                         resource_type=comment_file.file_resource_type,
                                         type=comment_file.file_type)
                        if result.get('result') != 'ok':
                            return Response(
                                {"message": f"Xoá file {comment_file.file_public_id} thất bại trên Cloudinary!"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                comment.delete()
                return Response({"message": "Xoá comment thành công"})
            return Response({"message": "Bạn không có quyền xoá comment này!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlogViewSet(viewsets.ViewSet, viewsets.generics.ListAPIView, viewsets.generics.CreateAPIView,
                  viewsets.generics.DestroyAPIView, viewsets.generics.UpdateAPIView):
    queryset = Blog.objects.all()
    serializer_class = serializers.BlogSerializer
    pagination_class = paginators.BlogPaginator
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @action(methods=['GET'], url_path='load-new-blogs', detail=False)
    def load_new_blogs(self, request, pk=None):
        results = []

        blogs = Blog.objects.all().order_by('-id')
        for blog in blogs:
            results.append({
                "blog_id": blog.id,
                "blog_title": blog.title,
                "blog_image": blog.image,
                "blog_description": blog.description,
                "blog_created_date": blog.created_date,
            })
        paginator = paginators.BlogHomePaginator()
        page = paginator.paginate_queryset(results, request)
        serializer = serializers.BlogsSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(methods=['GET'], url_path='info-details', detail=True)
    def get_details_info_blog(self, request, pk=None):
        blog = self.get_object()
        results = [{
            "blog_id": blog.id,
            "blog_title": blog.title,
            "blog_content": blog.content,
            "blog_created_date": blog.created_date,
        }]

        return Response({"results": serializers.BlogDetailsSerializer(results[0]).data}, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView,
                     generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = serializers.ProductSerializer
    pagination_class = paginators.ProductPaginator
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @action(methods=['GET'], url_path='load-product-home', detail=False)
    def load_product_home(self, request, pk=None):
        results = []

        products = Product.objects.filter(active=True)
        for product in products:
            tags = product.tags.all()
            results.append({
                "id_product": product.id,
                "id_category": product.category.id,
                "name_category": product.category.name,
                "image_product": product.image,
                "name_product": product.name,
                "unit_price_product": product.unit_price,
                "discount_product": product.discount,
                "present_price": product.unit_price - ((product.unit_price * product.discount) / 100),
                "tags_product": tags
            })

        paginator = paginators.ProductPaginator()
        page = paginator.paginate_queryset(results, request)
        serializer = serializers.ProductHomeSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(methods=['GET'], url_path='info-details', detail=True)
    def get_details_info_product(self, request, pk=None):
        product = self.get_object()
        users = User.objects.all()

        data_reviews = []

        for user in users:
            comments = Comment.objects.filter(product=product, user=user)
            for comment in comments:
                comment_files = []
                list_comment_files = CommentFile.objects.filter(comment=comment)
                for comment_file in list_comment_files:
                    comment_files.append({
                        "file_id": comment_file.id,
                        "file_name": comment_file.file_name,
                        "file_url": comment_file.file_url,
                        "file_resource_type": comment_file.file_resource_type,
                    })
                data_reviews.append({
                    "user_id": user.id,
                    "user_avatar": user.avatar,
                    "user_fullname": user.last_name + ' ' + user.first_name,
                    "comment_id": comment.id,
                    "comment_star": comment.star,
                    "comment_content": comment.content,
                    "comment_files": comment_files
                })

        data_related_products = []

        related_products = Product.objects.filter(category=product.category)

        for related_product in related_products:
            data_related_products.append({
                "id_product": related_product.id,
                "image_product": related_product.image,
                "name_product": related_product.name,
                "name_category": related_product.category.name,
                "unit_price_product": related_product.unit_price,
                "discount_product": related_product.discount,
                "present_price": related_product.unit_price - ((related_product.unit_price * related_product.discount)
                                                               / 100),
            })

        # Transform the color field into a list of dictionaries for the serializer
        color_list = [{"color_name": color} for color in product.color.split(" - ")]

        results = [{
            "id_product": product.id,
            "active_product": product.active,
            "image_product": product.image,
            "name_product": product.name,
            "color_product": color_list,
            "unit_price_product": product.unit_price,
            "discount_product": product.discount,
            "present_price": product.unit_price - ((product.unit_price * product.discount) / 100),
            "description_product": product.description,
            "related_products": data_related_products,
            "reviews": data_reviews,

        }]

        return Response(
            {"results": serializers.ProductDetailsSerializer(results, many=True).data},
            status=status.HTTP_200_OK
        )

    @action(methods=['post'], url_path='add-comment', parser_classes=[parsers.MultiPartParser], detail=True)
    def add_comment(self, request, pk=None):
        try:
            user = request.user
            product = self.get_object()
            content = request.data.get('content')
            star = request.data.get('star')
            files = request.FILES.getlist('files')
            allowed_mime_types = [
                'image/png',
                'image/jpeg',
                'image/gif',
                'image/bmp',
                'image/webp',
                'image/tiff',
                'image/svg+xml',
                'image/x-icon',
                'video/mp4',
                'video/webm',
                'video/x-msvideo',  # AVI
                'video/quicktime',  # MOV
                'video/mpeg',
                'video/x-matroska',  # MKV
                'video/3gpp',
                'video/3gpp2',
                'video/x-flv',
                'video/x-ms-wmv'
            ]
            file_urls_names = []

            if content and star:
                new_comment = Comment.objects.create(content=content, star=star, user=user,
                                                     product=product)
                if files:
                    for file in files:
                        if file.content_type in allowed_mime_types:
                            new_image_of_comment = cloudinary.uploader.upload(file, resource_type='auto')
                            file_urls_names.append({
                                "url": new_image_of_comment['secure_url'],
                                "name": file.name,
                                "public_id": new_image_of_comment['public_id'],
                                "asset_id": new_image_of_comment['asset_id'],
                                "resource_type": new_image_of_comment['resource_type'],
                                "type": new_image_of_comment['type'],

                            })
                    for url_name in file_urls_names:
                        CommentFile.objects.create(comment=new_comment, file_url=url_name["url"],
                                                   file_name=url_name["name"],
                                                   file_public_id=url_name["public_id"],
                                                   file_asset_id=url_name["asset_id"],
                                                   file_resource_type=url_name["resource_type"],
                                                   file_type=url_name["type"])
                    return Response({"message": "Thêm bình luận vào sản phẩm thành công!"},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Thêm bình luận vào sản phảm thất bại! Vui lòng thêm nội dung "
                                            "và đánh giá của bình luận"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], url_path='search', detail=False)
    def search_products_by_kw(self, request):
        keyword = request.query_params.get("keyword")
        products = Product.objects.filter(name__icontains=keyword)
        products = products.annotate(
            present_price_product=F('unit_price') - (F('unit_price') * F('discount') / 100)
        )
        data_products = []
        for product in products:
            data_products.append({
                "id_product": product.id,
                "name_product": product.name,
                # "unit_price_product": product.unit_price,
                "present_price_product": product.present_price_product,
                "image_product": product.image
            })
        paginator = paginators.ProductWithKeywordPaginator()
        page = paginator.paginate_queryset(data_products, request)
        serializer = serializers.ProductsWithKeywordSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PromotionTicketViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView,
                             generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = PromotionTicket.objects.filter(active=True)
    serializer_class = serializers.PromotionTicketSerializer
    pagination_class = paginators.PromotionTicketPaginator

    @action(methods=['get'], url_path='validate-promotion-ticket', detail=False)
    def validate_promotion_ticket(self, request):
        try:
            promotion_ticket_code = request.query_params.get('promotion_ticket_code')
            total_amount_order = str(request.query_params.get('total_amount_order'))
            promotion_ticket = PromotionTicket.objects.get(code=promotion_ticket_code)
            print(timezone.now())
            if promotion_ticket.expiry_date <= timezone.now():
                return Response({"message": f"Sử dụng phiếu giảm giá thất bại! "
                                            f"Phiếu giảm giá đã hết hạn sử dụng vào ngày "
                                            f"{promotion_ticket.expiry_date} "}
                                , status=status.HTTP_200_OK)

            if promotion_ticket.min_order_value > float(total_amount_order):
                return Response({"message": f"Sử dụng phiếu giảm giá thất bại! "
                                            f"Giá trị tổng công của đơn đặt hàng của bạn "
                                            f"không đạt đủ giá trị tối thiểu của phiếu giảm giá "
                                            f"là {promotion_ticket.min_order_value}"}, status=status.HTTP_200_OK)
            if Order.objects.filter(
                    promotion_ticket=promotion_ticket).count() >= promotion_ticket.expiry_number_used:
                return Response({"message": f"Sử dụng phiếu giảm giá thất bại! "
                                            f"Phiếu giảm giá này đã vượt quá số lần sử dụng "
                                            f"là {promotion_ticket.expiry_number_used} lần"},
                                status=status.HTTP_200_OK)
            return Response({"message": "Sử dụng phiếu giảm giá thành công!",
                             "discount_voucher": promotion_ticket.discount_price}, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({"message": "Sử dụng phiếu giảm giá thất bại! Mã của phiếu giảm giá không hợp lệ"},
                            status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    pagination_class = paginators.OrderDetailPaginator

    @action(methods=['get'], url_path='list-order-details', detail=True)
    def list_order_details(self, request, pk=None):
        order = self.get_object()
        orderDetails = OrderDetail.objects.filter(order=order)
        data = []
        for orderDetail in orderDetails:
            data.append({
                "order_detail_id": orderDetail.id,
                "order_detail_product_image": orderDetail.product.image,
                "order_detail_product_name": orderDetail.product.name,
                "order_detail_product_unit_price": orderDetail.product.unit_price,
                "order_detail_product_quantity": orderDetail.quantity,
                "order_detail_product_discount": orderDetail.product.discount,
                "order_detail_discount_price": orderDetail.discount_price,
                "order_detail_total_amount": orderDetail.total_amount,
            })
        paginator = paginators.OrderDetailPaginator()
        page = paginator.paginate_queryset(data, request)
        serializer = serializers.OrderDetailOfCustomerSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(methods=['patch'], url_path='update-status', detail=True)
    def update_status(self, request, pk=None):
        try:
            order = self.get_object()
            updated_status = request.data.get('updated_status')
            user = request.user
            confirm_statuses = ['Chờ xác nhận', 'Đã xác nhận', 'Đang xử lý',
                                'Đang giao hàng', 'Đã giao hàng', 'Đã hủy',
                                'Hoàn trả', 'Hoàn tiền', 'Thất bại']

            if user.role.name == "Quản trị viên":
                if updated_status:
                    if updated_status in confirm_statuses:
                        order.status = updated_status
                        order.updated_date = datetime.now()
                        order.save()
                        return Response({"messgae": f'Cập nhật trạng thái đơn hàng thành {updated_status} thành công!'},
                                        status=status.HTTP_200_OK)
                    else:
                        return Response({"message": f'Cập nhật trạng thái đơn hàng thành {updated_status} thất bại! '
                                                    f'Trạng thái không hợp lệ'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": f'Cập nhật trạng thái đơn hàng thất bại! Thiếu tham số trạng thái cập '
                                                f'nhật'}
                                    , status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": f'Cập nhật trạng thái đơn hàng thất bại! Người dùng không hợp lệ'},
                                status=status.HTTP_401_UNAUTHORIZED)
        except Exception as ex:
            return Response({"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
