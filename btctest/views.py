# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import Http404
from django.conf import settings
from django.utils import timezone
from django.views.generic import View
from django.core.mail import send_mail
from models import TX_Sent
from forms import TXForm, FindAddress, ConfirmToken
import blockcypher
import base64
import uuid


def generate_uuid(string_length=24):
    """Method usado para gerar chaves únicas, aplicadas ao TX_ID e Token
    """
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-", "")
    return random[0:string_length]


def validate_token(txid, token):
    """Method usado para validar Token da Transação
        txid = ID da transação registrada no BD
        token = token informado pelo usuário
    """
    tx_list = TX_Sent.objects.filter(tx_id=txid, status='P')
    if len(tx_list) == 1:
        tx_obj = tx_list[0]
        if tx_obj.confirm_token(token):
            tx_obj.status = 'C'
            tx_obj.token_confirmed = timezone.now()
            tx_obj.save()
            return tx_obj
    return None


def send_token_Email(tx_obj):
    """Method usado para enviar E-mail com token
        tx_obj = objeto TX_Sent, recém criado
    """
    btc_value = float(tx_obj.value) / 100000000
    btc_value = format(btc_value, ".9f")
    html_message = render_to_string('email_token.html', context={'tx': tx_obj, 'btc_value': btc_value})
    send_mail('BTC TEST - Token - Confirme a Transação', '', settings.EMAIL_FROM, [tx_obj.email], html_message=html_message)


def send_btc_transaction(tx_obj):
    """Method usado para propagar a transação na Blockchain
        tx_obj = objeto TX_Sent, confirmado pelo token
    """
    tx_hash = blockcypher.simple_spend(
        from_privkey=base64.b64decode(tx_obj.private_key_hashed),
        to_address=tx_obj.dest_addrs,
        to_satoshis=tx_obj.value,
        privkey_is_compressed=False,
        api_key=settings.BLOCKCYPHER_API_KEY,
        coin_symbol='btc-testnet'
    )
    return tx_hash


class CreateSendTX(View):
    """View responsável por criar Transação
        - Criar Transação TX, porém não envia para blockchain
        - Envia token no email informado
    """
    template_name = 'btc_send.html'
    form_class = TXForm

    def get(self, request):
        form = self.form_class()
        context_data = {'form': form, }
        return render(request, self.template_name, context_data)

    def post(self, request):
        form = self.form_class(request.POST or None)
        if form.is_valid():
            priv_key = form.cleaned_data['priv_key']
            dest_addr = form.cleaned_data['dest_addr']
            value = form.cleaned_data['value'] * 100000000
            email = form.cleaned_data['email']
            tx = TX_Sent()
            tx.tx_id = generate_uuid()
            tx.token = generate_uuid()
            tx.email = email
            tx.private_key_hashed = base64.b64encode(priv_key)
            tx.dest_addrs = dest_addr
            tx.value = value
            tx.save()
            send_token_Email(tx)
            return redirect('btctest:confirm_tx', txid=tx.tx_id)
        context_data = {'form': form, }
        return render(request, self.template_name, context_data)


class Confirm_TX(View):
    """View responsável por receber o Token, validar a transação e propagar na blockchain
    """
    template_name = 'btc_confirm_tx.html'
    form_class = ConfirmToken

    def get(self, request, txid):
        initial_data = {'txid' : txid}
        form = self.form_class(initial=initial_data)
        context_data = {'form': form, 'txid': txid}
        return render(request, self.template_name, context_data)

    def post(self, request, txid):
        form = self.form_class(request.POST or None)
        if form.is_valid():
            token = form.cleaned_data['token']
            tx_obj = validate_token(txid, token)
            if tx_obj != None:
                try:
                    hash = send_btc_transaction(tx_obj)
                    tx_obj.hash = hash
                except:
                    tx_obj.status = 'E'
                tx_obj.save()
                context_data = {'tx': tx_obj}
                return render(request, 'btc_send_confirmation.html', context_data)
            else:
                form.add_error('token', 'Token ou Transação Inválida!')
        context_data = {'form': form, 'txid': txid}
        return render(request, self.template_name, context_data)


def fast_tx_confirmation(request, txid, token):
    """View responsável por confirmar a Transação enviada por email (link)
        txid = TX ID registrada no banco de dados
        token = Token enviado para confirmação
    """
    tx_obj = validate_token(txid, token)
    if tx_obj != None:
        try:
            hash = send_btc_transaction(tx_obj)
            tx_obj.hash = hash
        except:
            tx_obj.status = 'E'
        tx_obj.save()
    context_data = {'tx': tx_obj}
    return render(request, 'btc_send_confirmation.html', context_data)



def View_Address(request, addr):
    """View responsável por mostrar detalhes de um endereço
        addr = endereço da blockchain
    """
    template_name = 'btc_address_detail.html'
    try:
        address_detail = blockcypher.get_address_full(addr, coin_symbol='btc-testnet')
    except:
        raise Http404('Endereço não encontrado')
    context_data = {
        'addr_detail': address_detail,
    }
    print len(address_detail['txs'])
    address_detail['txs'] = address_detail['txs'][:10]
    return render(request, template_name, context_data)


class Find_Address(View):
    """View responsável por procurar endereço na blockchain
    """
    template_name = 'btc_find_address.html'
    form_class = FindAddress

    def get(self, request):
        form = self.form_class()
        tx_list = TX_Sent.objects.all()
        context_data = {'form': form, 'tx_list': tx_list[:10]}
        return render(request, self.template_name, context_data)

    def post(self, request):
        form = self.form_class(request.POST or None)
        if form.is_valid():
            address = form.cleaned_data['address']
            return redirect('btctest:view_address', addr=address)
        context_data = {'form': form, }
        return render(request, self.template_name, context_data)