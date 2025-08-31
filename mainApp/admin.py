from django.contrib import admin
from django.utils.html import format_html
from mainApp.models import Service, SitterService, Ad, Pet, Order


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "pet", "image_thumb", "created_at")
    list_display_links = ("id", "name")
    list_filter = ("pet", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at", "image_preview")

    fieldsets = (
        (None, {
            'fields': ("name", "pet", "description")
        }),
        ("Image", {
            'fields': ("image", "image_preview"),
        }),
        ("Timestamps", {
            'fields': ("created_at", "updated_at")
        }),
    )

    def image_thumb(self, obj: Service):
        if obj.image:
            return format_html('<img src="{}" style="height:40px; width:auto; object-fit:cover;"/>', obj.image.url)
        return "-"
    image_thumb.short_description = "Image"

    def image_preview(self, obj: Service):
        if obj.image:
            return format_html('<img src="{}" style="max-height:180px; width:auto; object-fit:contain; border:1px solid #ddd; padding:4px;"/>', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(SitterService)
class SitterServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "service", "address", "rate", "created_at")
    list_filter = ("service", "user", "created_at")
    search_fields = ("user__username", "service__name", "address__city")
    autocomplete_fields = ("user", "service", "address")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ("id", "punch_line", "image_thumb", "url", "created_at")
    list_display_links = ("id", "punch_line")
    list_filter = ("created_at",)
    search_fields = ("punch_line",)
    readonly_fields = ("created_at", "updated_at", "image_preview")

    fieldsets = (
        (None, {
            'fields': ("punch_line", "url")
        }),
        ("Image", {
            'fields': ("image", "image_preview"),
        }),
        ("Timestamps", {
            'fields': ("created_at", "updated_at")
        }),
    )

    def image_thumb(self, obj: Ad):
        if obj.image:
            return format_html('<img src="{}" style="height:40px; width:auto; object-fit:cover;"/>', obj.image.url)
        return "-"
    image_thumb.short_description = "Image"

    def image_preview(self, obj: Ad):
        if obj.image:
            return format_html('<img src="{}" style="max-height:180px; width:auto; object-fit:contain; border:1px solid #ddd; padding:4px;"/>', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "pet", "breed", "age", "user", "image_thumb", "created_at")
    list_display_links = ("id", "name")
    list_filter = ("pet", "user", "created_at")
    search_fields = ("name", "breed", "user__username")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at", "image_preview")

    fieldsets = (
        (None, {
            'fields': ("user", "name", "pet", "breed", "age")
        }),
        ("Details", {
            'fields': ("bio", "important_info")
        }),
        ("Image", {
            'fields': ("image", "image_preview"),
        }),
        ("Timestamps", {
            'fields': ("created_at", "updated_at")
        }),
    )

    def image_thumb(self, obj: Pet):
        if obj.image:
            return format_html('<img src="{}" style="height:40px; width:auto; object-fit:cover;"/>', obj.image.url)
        return "-"
    image_thumb.short_description = "Image"

    def image_preview(self, obj: Pet):
        if obj.image:
            return format_html('<img src="{}" style="max-height:180px; width:auto; object-fit:contain; border:1px solid #ddd; padding:4px;"/>', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "normal_user", "petsitter_user", "service_model", "pet", "user_address", "quantity", "final_rate", "rating_for_petsitter", "rating_for_user", "status", "start_datetime", "created_at")
    list_display_links = ("id",)
    list_filter = ("status", "rating_for_petsitter", "rating_for_user", "start_datetime", "created_at")
    search_fields = ("normal_user__username", "petsitter_user__username", "service_model__service__name", "pet__name", "user_address__city")
    autocomplete_fields = ("normal_user", "petsitter_user", "service_model", "pet", "user_address")
    readonly_fields = ("final_rate", "created_at", "updated_at")

    fieldsets = (
        ("Order Details", {
            'fields': ("normal_user", "petsitter_user", "service_model", "pet", "user_address", "quantity", "final_rate", "start_datetime", "status")
        }),
        ("Messages", {
            'fields': ("msg_for_user", "msg_for_petsitter")
        }),
        ("Reviews & Ratings", {
            'fields': ("rating_for_petsitter", "rating_review_for_petsitter", "rating_for_user", "rating_review_for_user")
        }),
        ("Timestamps", {
            'fields': ("created_at", "updated_at")
        }),
    )
