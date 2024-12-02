from rest_framework import pagination


class ProductPaginator(pagination.PageNumberPagination):
    page_size = 10


class ProductOfCategoryPaginator(pagination.PageNumberPagination):
    page_size = 2


class ProductWithKeywordPaginator(pagination.PageNumberPagination):
    page_size = 2


class CategoryPaginator(pagination.PageNumberPagination):
    page_size = 4


class OriginPaginator(pagination.PageNumberPagination):
    page_size = 10


class TagPaginator(pagination.PageNumberPagination):
    page_size = 4


class CommentPaginator(pagination.PageNumberPagination):
    page_size = 5


class BlogPaginator(pagination.PageNumberPagination):
    page_size = 10


class BlogHomePaginator(pagination.PageNumberPagination):
    page_size = 4


class PromotionTicketPaginator(pagination.PageNumberPagination):
    page_size = 5


class OrderDetailPaginator(pagination.PageNumberPagination):
    page_size = 5


class OrdersOfCustomerPaginator(pagination.PageNumberPagination):
    page_size = 5