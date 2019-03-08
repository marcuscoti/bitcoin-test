# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from models import TX_Sent
from forms import FindAddress, TXForm
from views import generate_uuid
from django.urls import reverse
import base64

email_test = 'test@test.com'
addr_test = '2MtmDyW4z4rHhTCjuS8fBp1bW8SL7TxEEeb'
priv_key_test = '91kSA6JiwX6LE5j6CS7E1pndNGT1zCFzx8F8VFWqfchjkTnPMcF'

# Create your tests here.
class ModelTest(TestCase):

    def create_tx_skeleton(self):
        """Criar draft da TX"""
        tx = TX_Sent()
        tx.tx_id = generate_uuid(32)
        tx.token = generate_uuid(32)
        tx.email = email_test
        tx.private_key_hashed = base64.b64encode(priv_key_test)
        tx.dest_addrs = addr_test
        tx.value = 10000
        return tx

    def test_create_valid_TX(self):
        """Criar TX válida e criar TX duplicada"""
        tx = self.create_tx_skeleton()
        tx.save()
        tx_list = TX_Sent.objects.all()
        self.assertEqual(len(tx_list), 1, 'Erro na criação da TX')
        tx2 = self.create_tx_skeleton()
        tx2.tx_id = tx.tx_id
        with self.assertRaises(Exception) as cm:
            tx2.save()

    def test_TX_value(self):
        """Teste de Valor da TX"""
        tx = self.create_tx_skeleton()
        tx.save()
        tx = TX_Sent.objects.all()[0]
        self.assertEqual(tx.value, 10000, 'Erro no valor da TX')
        tx.value = 50000
        tx.save()
        tx = TX_Sent.objects.all()[0]
        self.assertEqual(tx.value, 50000, 'Erro no valor alterado da TX')


class ViewsTest(TestCase):

    def test_access_views(self):
        """Teste de acesso das views e urls"""
        resp = self.client.get(reverse("btctest:home"))
        self.assertEqual(resp.status_code, 200, 'Home view invalida')
        resp = self.client.get(reverse("btctest:send_btc"))
        self.assertEqual(resp.status_code, 200, 'Send BTC invalida')
        resp = self.client.get(reverse("btctest:find_address"))
        self.assertEqual(resp.status_code, 200, 'Procurar Endereço invalida')
        resp = self.client.get(reverse("btctest:view_address", kwargs={'addr': '2MtmDyW4z4rHhTCjuS8fBp1bW8SL7TxEEeb'}))
        self.assertEqual(resp.status_code, 200, 'Endereço incorreto')
        resp = self.client.get(reverse("btctest:view_address", kwargs={'addr': 'XXXXXXXXXXXXXXXXXXXXXXXXXXX'}))
        self.assertEqual(resp.status_code, 404, 'Endereço incorreto encontrado')


    def test_post_Create_TX(self):
        """Teste de post Create TX"""
        data = {
            'priv_key': priv_key_test,
            'dest_addr': addr_test,
            'value': 0.00002,
            'email': email_test,
            'email2': email_test,
        }
        response = self.client.post(reverse('btctest:send_btc'), data)
        self.assertEqual(response.status_code, 302, 'TX nao criada')
        tx = TX_Sent.objects.all()[0]
        data = {'token': tx.token}
        response = self.client.post(reverse("btctest:confirm_tx", kwargs={'txid': tx.tx_id}), data)
        self.assertEqual(response.status_code, 200, 'TX nao confirmada')

    def test_confirm_link(self):
        """Teste do link de confirmacao"""
        data = {
            'priv_key': priv_key_test,
            'dest_addr': addr_test,
            'value': 0.00002,
            'email': email_test,
            'email2': email_test,
        }
        self.client.post(reverse('btctest:send_btc'), data)
        tx = TX_Sent.objects.all()[0]
        response = self.client.get(reverse("btctest:fast_confirm", kwargs={'txid': tx.tx_id, 'token': tx.token}))
        self.assertEqual(response.status_code, 200, 'Link de confirmacao quebrado')


class FormTest(TestCase):

    def test_FindAddress_Form(self):
        """Teste do form Find Address"""
        data = {'address' : '2MtmDyW4z4rHhTCjuS8fBp1bW8SL7TxEEeb'}
        form = FindAddress(data=data)
        self.assertTrue(form.is_valid(), msg='Erro no Form FindAddress')
        data = {'address' : 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'}
        form = FindAddress(data=data)
        self.assertFalse(form.is_valid(), msg='Form FindAddress aceitou endereco incorreto')

    def test_TXForm_Form(self):
        """Teste do form TXForm"""
        data = {
            'priv_key': priv_key_test,
            'dest_addr': addr_test,
            'value': 0.00002,
            'email': email_test,
            'email2': email_test,
        }
        form = TXForm(data=data)
        self.assertTrue(form.is_valid(), msg='Erro no Form TXForm')
        data['dest_addr'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        form = TXForm(data=data)
        self.assertFalse(form.is_valid(), msg='Form TXForm Dest Addrs')
