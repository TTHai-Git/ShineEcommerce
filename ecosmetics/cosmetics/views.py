from datetime import datetime

import cloudinary
from django.core import paginator
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, parsers, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from unicodedata import decimal

from cosmetics import serializers, paginators
from cosmetics.models import *
from django.db.models import F, Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from ecosmetics import settings


def index(request):
    return HttpResponse("ScoreApp")


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

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
                    else:
                        setattr(user, k, v)
                user.save()
                return Response({'message': 'Cập nhật thông tin cá nhân thành công'}, status=status.HTTP_200_OK)
            else:
                return Response(serializers.UserSerializer(user).data)
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


class OriginsViewSet(viewsets.ViewSet, viewsets.generics.CreateAPIView, viewsets.generics.ListAPIView):
    queryset = Origin.objects.all()
    serializer_class = serializers.OriginSerializer
    pagination_class = paginators.OriginPaginator


class CategoryViewSet(viewsets.ViewSet, viewsets.generics.CreateAPIView, viewsets.generics.ListAPIView):
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
                "discount_product": f"{product.discount}%",
                "present_price": product.present_price,
            }
            for product in products
        ]

        # Handle pagination
        paginator = paginators.ProductPaginator()
        page = paginator.paginate_queryset(results, request)
        serializer = serializers.RelatedProductSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ViewSet, viewsets.generics.CreateAPIView, viewsets.generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = paginators.TagPaginator


class CommentViewSet(viewsets.ViewSet, viewsets.generics.CreateAPIView, viewsets.generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    pagination_class = paginators.CommentPaginator


class BlogViewSet(viewsets.ViewSet, viewsets.generics.ListAPIView):
    queryset = Blog.objects.all()
    serializer_class = serializers.BlogSerializer
    pagination_class = paginators.BlogPaginator
    parser_classes = [MultiPartParser]

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
        paginator = paginators.BlogPaginator()
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


class ProductViewSet(viewsets.ViewSet, viewsets.generics.CreateAPIView, viewsets.generics.ListAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = serializers.ProductSerializer
    pagination_class = paginators.ProductPaginator
    parser_classes = [MultiPartParser]

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
                "discount_product": str(product.discount) + "%",
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
                data_reviews.append({
                    "user_avatar": user.avatar,
                    "user_fullname": user.last_name + ' ' + user.first_name,
                    "comment_id": comment.id,
                    "comment_star": comment.star,
                    "comment_content": comment.content,
                })

        data_related_products = []

        related_products = Product.objects.filter(category=product.category)

        for related_product in related_products:
            data_related_products.append({
                "id_product": related_product.id,
                "image_product": related_product.image,
                "name_product": related_product.name,
                "unit_price_product": related_product.unit_price,
                "discount_product": str(related_product.discount) + "%",
                "present_price": related_product.unit_price -
                                 ((related_product.unit_price * related_product.discount) / 100),
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
            "discount_product": f"{product.discount}%",
            "present_price": product.unit_price - ((product.unit_price * product.discount) / 100),
            "description_product": product.description,
            "related_products": data_related_products,
            "reviews": data_reviews,

        }]

        return Response(
            {"results": serializers.ProductDetailsSerializer(results, many=True).data},
            status=status.HTTP_200_OK
        )
