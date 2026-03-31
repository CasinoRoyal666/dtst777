import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Record


def make_json_file(data):
    """creates a byte json file for uploading in form"""
    import io
    content = json.dumps(data, ensure_ascii=False).encode('utf-8')
    f = io.BytesIO(content)
    f.name = 'test.json'
    return f


class UploadViewValidationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('records:upload')

    #test with right data that passes validation
    def test_valid_data_saves_records(self):
        data = [
            {"name": "Alice", "date": "2024-03-15_14:30"},
            {"name": "Bob", "date": "2024-01-01_09:00"},
        ]
        response = self.client.post(self.url, {'file': make_json_file(data)})
        self.assertEqual(Record.objects.count(), 2)
        self.assertRedirects(response, reverse('records:list'))

    # test with extra key in data
    def test_extra_keys_are_ignored(self):
        data = [
            {"name": "Alice", "date": "2024-03-15_14:30", "extra": "ignored"},
        ]
        self.client.post(self.url, {'file': make_json_file(data)})
        self.assertEqual(Record.objects.count(), 1)

    # test validation -> if name field contains more that 50 chars then -> no save
    def test_name_too_long_saves_nothing(self):
        data = [
            {"name": "A" * 50, "date": "2024-03-15_14:30"},
        ]
        self.client.post(self.url, {'file': make_json_file(data)})
        self.assertEqual(Record.objects.count(), 0)

    # test validation -> incorrect date field format -> no save
    def test_invalid_date_format_saves_nothing(self):
        data = [
            {"name": "Alice", "date": "15-03-2024 14:30"},
        ]
        self.client.post(self.url, {'file': make_json_file(data)})
        self.assertEqual(Record.objects.count(), 0)

    # test validation -> no name field -> no save
    def test_missing_name_key_saves_nothing(self):
        data = [
            {"date": "2024-03-15_14:30"},
        ]
        self.client.post(self.url, {'file': make_json_file(data)})
        self.assertEqual(Record.objects.count(), 0)

    # test validation -> no date field -> no save 
    def test_missing_date_key_saves_nothing(self):
        data = [
            {"name": "Alice"},
        ]
        self.client.post(self.url, {'file': make_json_file(data)})
        self.assertEqual(Record.objects.count(), 0)

    # test validation -> if at least 1 record invalid -> no save (all records)
    def test_one_invalid_record_saves_nothing(self):
        data = [
            {"name": "Alice", "date": "2024-03-15_14:30"},
            {"name": "B" * 50, "date": "2024-01-01_09:00"},
        ]
        self.client.post(self.url, {'file': make_json_file(data)})
        self.assertEqual(Record.objects.count(), 0)

    # invalid JSON file test
    def test_invalid_json_file(self):
        import io
        bad_file = io.BytesIO(b'not a json at all')
        bad_file.name = 'bad.json'
        response = self.client.post(self.url, {'file': bad_file})
        self.assertEqual(Record.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    # JSON must be list '[]'
    def test_json_not_a_list(self):
        import io
        bad_file = io.BytesIO(b'{"name": "Alice", "date": "2024-03-15_14:30"}')
        bad_file.name = 'bad.json'
        response = self.client.post(self.url, {'file': bad_file})
        self.assertEqual(Record.objects.count(), 0)


class ListViewTests(TestCase):

    def test_list_page_returns_200(self):
        response = self.client.get(reverse('records:list'))
        self.assertEqual(response.status_code, 200)

    def test_list_shows_records(self):
        Record.objects.create(name="Alice", date="2024-03-15 14:30:00")
        response = self.client.get(reverse('records:list'))
        self.assertContains(response, "Alice")