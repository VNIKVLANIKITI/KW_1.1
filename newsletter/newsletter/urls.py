from django.contrib import admin
from django.urls import path
from letters.views import health_check
from .views import health_check as health_general
from letters.views import get_customer_list as get_customer_list
from letters.views import get_mailing_list as get_mailing_list
from letters.views import get_message_list as get_message_list

from letters.views import MailingCreateView, MailingDeleteView, mailing_report, MessageCreateView, MessageDeleteView, MessageUpdateView, СustomerCreateView, CustomerDeleteView, СustomerUpdateView, MessageSend
from django.urls import include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("letters/alive", health_check),
    path("letters/all", health_check),
    path("general/home", health_general),
    path("", get_customer_list, name='customer_list'),
    path("customer/create", СustomerCreateView.as_view(), name='create_customer'),
    path('customer/delete/<int:pk>', CustomerDeleteView.as_view(),
         name='customer_delete'),
    path('customer/<int:pk>', СustomerUpdateView.as_view(),
         name='customer_update'),


    
    path("mailing/list", get_mailing_list, name='mailing_list'),

    path("mailing/create", MailingCreateView.as_view(), name='create_mailing'),
    path('mailing/delete/<int:pk>', MailingDeleteView.as_view(),
         name='mailing_delete'),

    path("message/list", get_message_list, name='message_list'),
    path("message/create", MessageCreateView.as_view(), name='create_message'),
    path('message/delete/<int:pk>', MessageDeleteView.as_view(),
         name='message_delete'),
    path('message/<int:pk>', MessageUpdateView.as_view(),
         name='message_update'),
    path('mailing/send/<int:pk>', MessageSend, name='mailing_send'),

    path('mailing/report/', mailing_report, name='mailing_report'),
    path('users/', include('users.urls', namespace='users')),
]
