# reports/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reports'

urlpatterns = [
    # Report management
    path('create/', views.ReportCreateView.as_view(), name='report-create'),
    path('list/', views.ReportListView.as_view(), name='report-list'),
    path('<uuid:id>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('<uuid:id>/progress/', views.ReportProgressView.as_view(), name='report-progress'),
    path('<uuid:id>/delete/', views.ReportDeleteView.as_view(), name='report-delete'),

    # Report sharing
    path('<uuid:report_id>/share/', views.ReportShareCreateView.as_view(), name='report-share-create'),
    path('shared/<uuid:share_token>/', views.SharedReportView.as_view(), name='shared-report'),

    # Website management
    path('websites/', views.WebsiteListView.as_view(), name='website-list'),
    path('websites/<int:pk>/', views.WebsiteDetailView.as_view(), name='website-detail'),

    # Report templates
    path('templates/', views.ReportTemplateListView.as_view(), name='template-list'),

    # Analytics and utilities
    path('analytics/', views.ReportAnalyticsView.as_view(), name='report-analytics'),
    path('validate-url/', views.validate_website_url, name='validate-url'),
]