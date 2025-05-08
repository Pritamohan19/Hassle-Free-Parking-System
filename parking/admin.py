import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import (
    Area, SubArea, ParkingSlot,
    LoginRegisterLog, UserAuthenticationRegistration,
    Contact, Feedback
)
from parking.models import Booking
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Inline configuration for SubArea within Area
class SubAreaInline(admin.TabularInline):
    model = SubArea
    extra = 1

# Inline configuration for ParkingSlot within SubArea
class ParkingSlotInline(admin.TabularInline):
    model = ParkingSlot
    extra = 1

# Area Admin
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [SubAreaInline]

# SubArea Admin
class SubAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'description')
    search_fields = ('name', 'area__name')
    ordering = ('area', 'name')
    inlines = [ParkingSlotInline]

# ParkingSlot Admin
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('slot_number', 'sub_area', 'is_available')
    list_filter = ('sub_area', 'is_available')
    search_fields = ('slot_number', 'sub_area__name')
    ordering = ('sub_area', 'slot_number')

# Booking Admin
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'parking_slot', 'vehicle_number', 'start_time', 'end_time')
    list_filter = ('parking_slot', 'start_time', 'end_time')
    search_fields = ('user__username', 'vehicle_number', 'parking_slot__slot_number')
    ordering = ('start_time', 'end_time')

# Customize the User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

# CSV Export Mixin
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.model_name}.csv'  # Use model_name for cleaner file name
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field in field_names:
                value = getattr(obj, field)
                # Handle foreign keys
                if hasattr(value, 'username'):  # For User foreign key
                    value = value.username
                row.append(value)
            writer.writerow(row)

        return response

    export_as_csv.short_description = "Export Selected as CSV"

# Replace default User with customized
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)

# Register Area-related models
admin.site.register(Area, AreaAdmin)
admin.site.register(SubArea, SubAreaAdmin)
admin.site.register(ParkingSlot, ParkingSlotAdmin)
admin.site.register(Booking, BookingAdmin)

# Login/Register Log Admin
@admin.register(LoginRegisterLog)
class LoginRegisterLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'action', 'timestamp')

    def get_email(self, obj):
        return obj.user.email if obj.user and obj.user.email else "-"
    get_email.short_description = 'Email'

    search_fields = ('user__username', 'action')
    ordering = ('-timestamp',)

# User Auth Registration Admin
@admin.register(UserAuthenticationRegistration)
class UserAuthenticationRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'action', 'timestamp')

# Contact Admin
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'timestamp')
    search_fields = ('name', 'email')
    ordering = ('-timestamp',)

# Feedback Admin with export functionality
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('get_user', 'rating', 'goal_achievement', 'reason', 'submitted_on')
    search_fields = ('user__username', 'comments', 'suggestions')
    list_filter = ('rating', 'goal_achievement', 'reason', 'issue', 'is_public', 'submitted_on')
    ordering = ('-submitted_on',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Feedback Rating', {
            'fields': ('rating',)
        }),
        ('Feedback Details', {
            'fields': ('comments', 'goal_achievement', 'reason', 'issue', 'suggestions')
        }),
        ('Admin Settings', {
            'fields': ('is_public', 'submitted_on')
        }),
    )
    
    readonly_fields = ('submitted_on',)
    actions = ['export_as_csv']
    
    def get_user(self, obj):
        return obj.user.username if obj.user else "Anonymous"
    get_user.short_description = 'User'
    get_user.admin_order_field = 'user__username'
