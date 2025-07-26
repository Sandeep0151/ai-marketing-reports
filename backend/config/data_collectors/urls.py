# data_collectors/urls.py
from django.urls import path
from . import views

app_name = 'data_collectors'

urlpatterns = [
    # Basic website analysis
    path('analyze-website/', views.AnalyzeWebsiteView.as_view(), name='analyze-website'),
    path('test-connection/', views.TestAPIConnectionView.as_view(), name='test-connection'),

    # Individual data collection endpoints
    path('seo-data/', views.CollectSEODataView.as_view(), name='collect-seo'),
    path('social-data/', views.CollectSocialDataView.as_view(), name='collect-social'),
    path('reputation-data/', views.CollectReputationDataView.as_view(), name='collect-reputation'),
    path('competitor-data/', views.CollectCompetitorDataView.as_view(), name='collect-competitor'),
]