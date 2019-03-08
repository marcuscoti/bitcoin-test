# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse


# Create your models here.
class TX_Sent(models.Model):

    STATUS_C = (
        ('P', 'Pending'),
        ('C', 'Confirmed'),
        ('E', 'Error'),
    )

    tx_id = models.CharField(max_length=24, unique=True)
    hash = models.CharField(max_length=24, null=True, blank=True)
    value = models.BigIntegerField(validators=[MinValueValidator(1)])
    private_key_hashed = models.CharField(max_length=256, null=True, blank=True)
    dest_addrs = models.CharField(max_length=256)
    email = models.EmailField()
    token = models.CharField(max_length=256)
    status = models.CharField(max_length=11, choices=STATUS_C, default='P')
    created = models.DateTimeField(auto_now_add=True)
    token_confirmed = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.tx_id

    def __str__(self):
        return self.tx_id

    def confirm_token(self, token):
        """Method usado para confirmar o Token registrado da transação"""
        if token==self.token:
            return True
        else:
            return False

    def confirm_link(self):
        """Method usado para adquirir o link de confirmação no email"""
        return reverse('btctest:fast_confirm', kwargs={'txid': self.tx_id, 'token': self.token})


    def get_status(self):
        """Method usado para adquirir a descrição do STATUS"""
        for value in self.STATUS_C:
            if value[0] == self.status:
                return value[1]



    class Meta:
        verbose_name_plural = "Transactions"