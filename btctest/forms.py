# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
import blockcypher


#Form usado para criar o envio da transação
class TXForm(forms.Form):
    priv_key = forms.CharField(label='Private Key (sem compressão)')
    dest_addr = forms.CharField(label='Endereço de Destino')
    value = forms.FloatField(label='Valor', max_value=1, min_value=0)
    email = forms.EmailField(label='Email para confirmação')
    email2 = forms.EmailField(label='Confirme seu email')

    def clean(self, *args, **kwargs):
        if not self.cleaned_data['email'] == self.cleaned_data['email2']:
            self.add_error('email', 'Os e-mails devem ser iguais!')

        if self.cleaned_data['value'] == 0:
            self.add_error('value', 'O valor deve ser maior que 0 e menor que 1!')

        first_char = self.cleaned_data['dest_addr'][0]
        if not blockcypher.is_valid_address(self.cleaned_data['dest_addr']):
            self.add_error('dest_addr', 'Endereço de destino inválido!')
        else:
            if not first_char == '2' or first_char == 'm' or first_char == 'n':
                self.add_error('dest_addr', 'Este Endereço não é da TesteNet3!')

        first_char = self.cleaned_data['priv_key'][0]
        if not first_char == '9':
            self.add_error('priv_key', 'Esta Private Key não é da TesteNet3 ou está Comprimida!')

        return super(TXForm, self).clean(*args, **kwargs)


#Form usado para procurar endereço e mostrar detalhes
class FindAddress(forms.Form):
    address = forms.CharField(label='Endereço')

    def clean(self, *args, **kwargs):
        if not blockcypher.is_valid_address(self.cleaned_data['address']):
            self.add_error('address', 'Endereço Não Encontrado!')
        return super(FindAddress, self).clean(*args, **kwargs)


#Form usado para confirmar Token
class ConfirmToken(forms.Form):
    token = forms.CharField(label='Token recebio no email')