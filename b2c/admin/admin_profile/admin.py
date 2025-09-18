from django.contrib import admin
from .models import AdminProfile, CompanyDetails, EmailSecurity


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name", "job_title")
    search_fields = ("user__username", "first_name", "last_name", "job_title")
    list_filter = ("job_title",)
    ordering = ("id",)


@admin.register(CompanyDetails)
class CompanyDetailsAdmin(admin.ModelAdmin):
    list_display = ("id", "company_name", "industry_type", "company_email", "company_phone")
    search_fields = ("company_name", "company_email", "company_phone")
    list_filter = ("industry_type",)
    ordering = ("id",)


@admin.register(EmailSecurity)
class EmailSecurityAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "backup_email")
    search_fields = ("user__username", "backup_email")
    ordering = ("id",)
