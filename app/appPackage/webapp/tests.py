from django.test import TestCase

from .models import *

# Create your tests here.
class ModelTests(TestCase):

    def test_randomtest(self):
        self.assertIs(True, True)
