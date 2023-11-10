from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from market_place.models import StorageBox
from booking.models import Booking


class SurfaceFilter(admin.SimpleListFilter):
    title = "surface range"
    parameter_name = "surface"

    def lookups(self, request, model_admin):
        return (
            ("0-4", "0-4 m2"),
            ("5-9", "5-9 m2"),
            ("10-19", "10-19 m2"),
            ("20<=", "20 m2 and over"),
        )

    def queryset(self, request, queryset):
        if self.value() == "0-4":
            return queryset.filter(surface__lte=4)
        if self.value() == "5-9":
            return queryset.filter(surface__range=(5, 9))
        if self.value() == "10-19":
            return queryset.filter(surface__range=(10, 20))
        if self.value() == "20<=":
            return queryset.filter(surface__gte=20)


class CustomDateRangeFilter(DateRangeFilter):
    def queryset(self, request, queryset):
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data:
                date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
                date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)
                not_available_storage_box = Booking.objects.filter(
                    start_date__lte=date_value_lte, end_date__gte=date_value_gte
                )
                not_available_box_id = not_available_storage_box.values(
                    "storage_box__id"
                )
                return queryset.exclude(id__in=not_available_box_id)
        return queryset


def CustomDateRangeFilterBuilder(title=None, default_start=None, default_end=None):
    filter_cls = type(
        str("CustomDateRangeFilter"),
        (CustomDateRangeFilter,),
        {
            "__from_builder": True,
            "default_title": title,
            "default_start": default_start,
            "default_end": default_end,
        },
    )

    return filter_cls


@admin.register(StorageBox)
class StorageBoxAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "surface", "created_on")
    list_filter = (
        SurfaceFilter,
        ("id", CustomDateRangeFilterBuilder(title="Available dates")),
    )
    ordering = ["-created_on"]

    @admin.display()
    def start_date(self, obj):
        return obj.storage_box.title
