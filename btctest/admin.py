# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models import TX_Sent
from django.contrib import admin


# Register your models here.
class TX_SentAdmin(admin.ModelAdmin):
    class Meta:
        model = TX_Sent

    list_display = ('hash', 'value', 'dest_addrs', 'email', 'token', 'status', 'created', 'token_confirmed')
    list_display_links = ('hash', 'value', 'dest_addrs', 'email', 'token', 'status', 'created', 'token_confirmed')
    list_filter = ('status',)
    search_filters = ('hash', 'dest_addrs', 'email', 'token',)


admin.site.register(TX_Sent, TX_SentAdmin)