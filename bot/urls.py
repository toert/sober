
from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^$', views.render_dashboard, name='render_dashboard'),
    url(r'^ad/$', views.create_bot, name='create_bot'),
    url(r'^ad/(?P<bot_id>\d+)$', views.change_bot_from_vertical, name='change_bot_from_vertical'),
    url(r'^set_hmac/$', views.set_keys_page, name='set_keys_page'),
    url(r'^edit/(?P<bot_id>\d+)$', views.edit_ad, name='edit_ad'),
    url(r'^table/$', views.update_table, name='update_table'),

]


