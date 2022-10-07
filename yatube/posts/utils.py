from django.core.paginator import Paginator


PAGINATOR_PAGE = 10


def get_page(queryset, request):
    paginator = Paginator(queryset, PAGINATOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
