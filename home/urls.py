from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('newsletter/', views.newsletter_signup, name='newsletter_signup'),
    path('who-we-are/', views.who_we_are, name='who_we_are'),
    path('contact/', views.contact, name='contact'),
    path('sitemap.xml', views.serve_sitemap, name='sitemap'),
]