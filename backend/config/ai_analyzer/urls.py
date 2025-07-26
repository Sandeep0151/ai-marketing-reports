# ai_analyzer/urls.py
from django.urls import path
from . import views

app_name = 'ai_analyzer'

urlpatterns = [
    # AI analysis endpoints
    path('calculate-trust-score/', views.CalculateTrustScoreView.as_view(), name='calculate-trust-score'),
    path('generate-summary/', views.GenerateSummaryView.as_view(), name='generate-summary'),
    path('growth-recommendations/', views.GrowthRecommendationsView.as_view(), name='growth-recommendations'),
    path('content-analysis/', views.ContentAnalysisView.as_view(), name='content-analysis'),

    # AI utilities
    path('test-openai/', views.TestOpenAIView.as_view(), name='test-openai'),
]