from django.test import Client
import datetime
import pytest
from pytest_django.asserts import assertTemplateUsed
from django.core.management import call_command


from market_place.views import get_search_params, filter_booking_boxes
from market_place.models import StorageBox


@pytest.fixture
@pytest.mark.django_db
def load_storage_data():
    call_command("loaddata", "fixtures/sample.json")


@pytest.fixture
@pytest.mark.django_db
def load_booking_data():
    call_command("loaddata", "../booking/fixtures/sample.json")


@pytest.mark.django_db
def test_get(client: Client) -> None:
    response = client.get("/market-place/", {"city": "Arnaud"})

    assert response.status_code == 200
    assertTemplateUsed(response, "market_place/index.html")


@pytest.mark.parametrize(
    "start_date, end_date, booked_boxes",
    (
        ("2023-10-23", "2023-12-23", 5),
        ("1996-10-23", "2000-12-23", 0),
        ("2023-06-10", "2023-06-20", 1),
        ("2023-07-13", "2023-07-15", 4),
    ),
)
@pytest.mark.django_db
def test_filter_date_range(
    load_storage_data,
    load_booking_data,
    start_date: str,
    end_date: str,
    booked_boxes: int,
) -> None:
    boxes = StorageBox.objects.all()
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    query_set = filter_booking_boxes(boxes, start_date, end_date)
    assert len(query_set) == len(boxes) - booked_boxes


@pytest.mark.parametrize(
    "url, excepted_params",
    (
        ("", ""),
        ("bdz", "bdz"),
        ("sort='filtre'&bdz", "bdz"),
        ("sort=''&bdz", "bdz"),
        ("city='bdz'", "city='bdz'"),
        ("sort=price_dsc&", ""),
        ("sort=surface_dsc&city=&start_date=&end_date=&storage_type=&min_size=0&max_size=17&min_price=18&max_price=56",
         "city=&start_date=&end_date=&storage_type=&min_size=0&max_size=17&min_price=18&max_price=56"),
        ("city=bdz&sort=price_dsc&", "city=bdz&sort=price_dsc&"),
    ),
)
def test_get_search_params(url: str, excepted_params: str) -> None:
    result = get_search_params(url)
    assert result == excepted_params
