from django.contrib import admin
from userApp.models import UserProfile, Address


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'name', 'role', 'phone_number', 'verified', 'created_at'
    )
    list_display_links = ('id', 'username')
    list_editable = ('verified',)
    list_filter = ('role', 'verified', 'created_at')
    search_fields = ('username', 'email', 'name', 'phone_number', 'pan', 'aadhar')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'role', 'verified')
        }),
        ('Identifiers', {
            'fields': ('email', 'username', 'phone_number')
        }),
        ('Documents (optional)', {
            'fields': ('pan', 'aadhar')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'address', 'city', 'state', 'zipcode', 'country', 'latitude', 'longitude', 'created_at'
    )
    list_display_links = ('id', 'user')
    list_filter = ('country', 'state', 'city', 'created_at')
    search_fields = ('user__username', 'user__email', 'address', 'city', 'state', 'zipcode', 'country')
    readonly_fields = ('created_at', 'updated_at')
