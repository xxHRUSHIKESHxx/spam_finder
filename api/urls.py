# api/urls.py
from django.urls import path
from .views import register, login, contact_list_create, contact_detail, search_by_name, search_by_phone_number, contact_detail_public, mark_as_spam

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),

    path('contacts/', contact_list_create, name='contacts'),
    path('contacts/<int:pk>/', contact_detail, name='contact-detail'),
    path('contacts/public/<int:pk>/', contact_detail_public,
         name='contact-detail-public'),
    path('search/name/<str:name>/', search_by_name, name='search-by-name'),
    path('search/phone/<str:phone_number>/',
         search_by_phone_number, name='search-by-phone'),
    path('mark_as_spam/', mark_as_spam, name='mark-as-spam'),

]
