import os
from django.test import TestCase
import mock
from frontend.utils.organisation import get_abbreviation


class TestUtilsOrganisation(TestCase):

    def test_get_abbreviation_one_word(self):
        abbreviation = get_abbreviation('CapeVerdeNature')
        self.assertEqual(abbreviation, 'CA')

    def test_get_abbreviation_multiple_word(self):
        abbreviation = get_abbreviation('Cape Verde Nature')
        self.assertEqual(abbreviation, 'CVN')
