
from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^$', views.render_dashboard, name='render_dashboard'),
    url(r'^create/$', views.create_bot, name='create_bot'),
    url(r'^set_hmac/$', views.set_keys_page, name='set_keys_page'),
    url(r'^edit/(?P<bot_id>\d+)$', views.edit_ad, name='edit_ad')
]


