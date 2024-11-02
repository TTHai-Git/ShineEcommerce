from rest_framework import pagination


class ProductPaginator(pagination.PageNumberPagination):
    page_size = 4


class CategoryPaginator(pagination.PageNumberPagination):
    page_size = 4


class OriginPaginator(pagination.PageNumberPagination):
    page_size = 10


class TagPaginator(pagination.PageNumberPagination):
    page_size = 4


class CommentPaginator(pagination.PageNumberPagination):
    page_size = 5


class BlogPaginator(pagination.PageNumberPagination):
    page_size = 5
