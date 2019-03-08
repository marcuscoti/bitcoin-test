# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from views import View_Address, Find_Address, CreateSendTX, Confirm_TX, send_token_Email, fast_tx_confirmation

urlpatterns = [
    url(r'^$', Find_Address.as_view(), name='home'),
    url(r'^address/(?P<addr>[\w-]+)/$', View_Address, name='view_address'),
    url(r'^findaddress/$', Find_Address.as_view(), name='find_address'),
    url(r'^send/$', CreateSendTX.as_view(), name='send_btc'),
    url(r'^confirm/(?P<txid>[\w-]+)/$', Confirm_TX.as_view(), name='confirm_tx'),
    url(r'^fastconfirm/(?P<txid>[\w-]+)/(?P<token>[\w-]+)/$', fast_tx_confirmation, name='fast_confirm'),
    url(r'^sendemail/(?P<txid>[\w-]+)/$', send_token_Email, name='send_email'),
]
