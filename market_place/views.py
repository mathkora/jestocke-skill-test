import datetime
from django.shortcuts import render
from django.db.models import Max, Min, QuerySet
import re


from market_place.models import StorageBox
from market_place.constants import StorageTypes
from booking.models import Booking


def get_search_params(url: str) -> str:
    start_params_index = 0
    sorted_regex = r"sort=.*?&"
    if re.match(sorted_regex, url):
        start_params_index = re.match(sorted_regex, url).span()[1]
    return url[start_params_index:]


def filter_booking_boxes(
    boxes: QuerySet, start_date: datetime.datetime, end_date: datetime.datetime
) -> QuerySet:
    not_available_boxes = Booking.objects.filter(
        start_date__lte=end_date, end_date__gte=start_date
    )
    not_available_box_id = not_available_boxes.values("storage_box__id")
    return boxes.exclude(id__in=not_available_box_id)


def storage(request):
    search_params = get_search_params(request.META["QUERY_STRING"])

    available_boxes = StorageBox.objects.all()
    start_date = None
    end_date = None

    if request.GET.get("city"):
        available_boxes = available_boxes.filter(city__contains=request.GET.get("city"))
    if request.GET.get("start_date"):
        start_date = datetime.datetime.strptime(
            request.GET.get("start_date"), "%Y-%m-%d"
        )
    if request.GET.get("end_date"):
        end_date = datetime.datetime.strptime(request.GET.get("end_date"), "%Y-%m-%d")
    if start_date and end_date:
        available_boxes = filter_booking_boxes(available_boxes, start_date, end_date)

    min_size = available_boxes.aggregate(Min("surface"))["surface__min"]
    max_size = available_boxes.aggregate(Max("surface"))["surface__max"]
    min_size_set = min_size
    max_size_set = max_size

    min_price = available_boxes.aggregate(Min("monthly_price"))["monthly_price__min"]
    max_price = available_boxes.aggregate(Max("monthly_price"))["monthly_price__max"]
    min_price_set = min_price
    max_price_set = max_price

    if request.GET.get("storage_type"):
        available_boxes = available_boxes.filter(
            storage_type=request.GET.get("storage_type")
        )

    if request.GET.get("min_size"):
        available_boxes = available_boxes.filter(
            surface__gte=request.GET.get("min_size")
        )
        min_size_set = request.GET.get("min_size")

    if request.GET.get("max_size"):
        available_boxes = available_boxes.filter(
            surface__lte=request.GET.get("max_size")
        )
        max_size_set = request.GET.get("max_size")

    if request.GET.get("min_price"):
        available_boxes = available_boxes.filter(
            monthly_price__gte=request.GET.get("min_price")
        )
        min_price_set = request.GET.get("min_price")

    if request.GET.get("max_price"):
        available_boxes = available_boxes.filter(
            monthly_price__lte=request.GET.get("max_price")
        )
        max_price_set = request.GET.get("max_price")

    if request.GET.get("sort"):
        if request.GET.get("sort") == "surface_asc":
            available_boxes = available_boxes.order_by("surface")
        if request.GET.get("sort") == "surface_dsc":
            available_boxes = available_boxes.order_by("-surface")
        if request.GET.get("sort") == "price_asc":
            available_boxes = available_boxes.order_by("monthly_price")
        if request.GET.get("sort") == "price_dsc":
            available_boxes = available_boxes.order_by("-monthly_price")

    return render(
        request,
        "market_place/index.html",
        context={
            "boxes": available_boxes,
            "now": datetime.date.today().strftime("%Y-%m-%d"),
            "tomorrow": (datetime.date.today() + datetime.timedelta(days=1)).strftime(
                "%Y-%m-%d"
            ),
            "cities": StorageBox.objects.values("city"),
            "choices": StorageTypes.choices,
            "min_size": min_size,
            "max_size": max_size,
            "min_price": min_price,
            "max_price": max_price,
            "nb_results": len(available_boxes),
            "min_size_set": min_size_set,
            "max_size_set": max_size_set,
            "min_price_set": min_price_set,
            "max_price_set": max_price_set,
            "search_params": search_params,
        },
    )
