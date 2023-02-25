from django.test import TestCase
from django.test import Client
from LegacySite.models import *
from LegacySite.views import *
from . import extras
from io import StringIO

# Create your tests here.

class MyTest(TestCase):
    # Django's test run with an empty database. We can populate it with
    # data by using a fixture. You can create the fixture by running:
    #    mkdir LegacySite/fixtures
    #    python manage.py dumpdata LegacySite > LegacySite/fixtures/testdata.json
    # You can read more about fixtures here:
    #    https://docs.djangoproject.com/en/4.0/topics/testing/tools/#fixture-loading
    fixtures = ["testdata.json"]

    # Assuming that your database had at least one Card in it, this
    # test should pass.
    def setUp(self):
        self.client = Client()
        self.SALT_LEN=16
        self.client.post('/register.html', {'uname':'komal2', 'pword':'komal2', 'pword2':'komal2'})
        

    def test_xss(self):
        response = self.client.get('/gift.html', {'director' : '<script>XSS attack.</script>'})
        self.assertTrue(response.status_code, 200)
        self.assertContains(response, "&lt;script&gt;XSS attack.&lt;/script&gt;")

    def test_giftattack(self):
        response = self.client.get('/buy.html', {'director' : '<form action=http://127.0.0.1:8000/gift/0 method=POST><input type=hidden name=amount value=450><input type=hidden name=username value=abcd><input type=submit value=Login></form>'})
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'item-single.html')

    def test_sqlinjection(self):
        self.client.login(username = 'komal2', password = 'komal2')
        attack3 = StringIO('{"merchant_id": "NYU Apparel Card", "customer_id": "komal", "total_value": 95, "records": [{"record_type": "amount_change", "amount_added": 2000, "signature": "26ecce438d9e278ea89cf55dbb22923c%\' UNION SELECT password FROM LegacySite_user WHERE LegacySite_user.username like \'%"}]}')
        data = {
               'card_data' : attack3,
               'card_supplied': True,
               'card_fname': 'randcard',
               }
        response = self.client.post('/use.html', data)
        self.assertNotContains(response, 'komal2')
        self.client.logout()

    def test_goodsalt(self):
        self.assertNotEqual(extras.generate_salt(self.SALT_LEN), extras.generate_salt(self.SALT_LEN))
