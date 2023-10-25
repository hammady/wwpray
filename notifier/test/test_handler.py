import unittest
from unittest.mock import patch
import os
from copy import deepcopy as cp
from handler import detect_changes, read_json, datetime
from datetime import datetime


class TestHandler(unittest.TestCase):
    def setUp(self):
        self.mocked_now = datetime(2022, 10, 24, 0, 0, 0)
        self.base_masjid = {
            "iqamas": {
                "fajr": {"time": "05:00"},
                "maghrib": {"time": "18:00"}
            },
            "jumas": ["12:30"],
            "last_updated": "2020-05-01T00:00:00"
        }

        self.masjid_with_fajr_changed = cp(self.base_masjid)
        self.masjid_with_fajr_changed["iqamas"]["fajr"]["time"] = "05:05"

        self.masjid_with_maghrib_changed = cp(self.base_masjid)
        self.masjid_with_maghrib_changed["iqamas"]["maghrib"] = {"time": "18:05"}

        self.masjid_with_jumas_changed = cp(self.base_masjid)
        self.masjid_with_jumas_changed["jumas"] = ["13:30", "14:30"]

        self.masjid_with_fajr_and_magrib_changed = cp(self.masjid_with_fajr_changed)
        self.masjid_with_fajr_and_magrib_changed["iqamas"]["maghrib"] = {"time": "18:05"}

        self.masjid_with_no_fajr = cp(self.base_masjid)
        del self.masjid_with_no_fajr["iqamas"]["fajr"]

        self.masjid_with_no_iqamas = cp(self.base_masjid)
        del self.masjid_with_no_iqamas["iqamas"]

        self.masjid_with_changed_on = cp(self.base_masjid)
        self.masjid_with_changed_on["iqamas"]["fajr"]["changed_on"] = "2020-04-01"

        self.test_saved_file = 'test.json'

    def tearDown(self):
        try:
            os.remove(self.test_saved_file)
        except:
            pass

    @patch('handler.datetime')
    def test_detect_changes_when_no_changes_return_none_but_save_new_data(self, datetime_mock):
        datetime_mock.datetime.utcnow.return_value = self.mocked_now
        changes = detect_changes(
            old_data={
                "masjids": {"m1": self.base_masjid}
            },
            new_data={
                "masjids": {"m1": self.base_masjid}
            },
            save_to_file=self.test_saved_file)
        self.assertIsNone(changes)
        saved_data = read_json(self.test_saved_file)
        self.assertEqual(saved_data["masjids"]["m1"]["iqamas"], self.base_masjid["iqamas"])
        self.assertEqual(saved_data["masjids"]["m1"]["jumas"], self.base_masjid["jumas"])
        self.assertEqual(saved_data["masjids"]["m1"].get("last_updated"), self.mocked_now.isoformat())

    @patch('handler.datetime')
    def test_detect_changes_when_fajr_changed_return_one_change(self, datetime_mock):
        datetime_mock.datetime.utcnow.return_value = self.mocked_now
        changes = detect_changes(
            old_data={
                "masjids": {"m1": self.base_masjid, "m2": self.base_masjid}
            },
            new_data={
                "masjids": {"m1": self.masjid_with_fajr_changed, "m2": self.base_masjid}
            },
            save_to_file=self.test_saved_file)
        self.assertEqual(len(changes), 1)
        self.assertIn("m1", changes)
        self.assertEqual(changes["m1"]["iqamas"]["fajr"].get("changed"), True)
        saved_data = read_json(self.test_saved_file)
        self.assertEqual(saved_data["masjids"]["m1"].get("last_updated"), self.mocked_now.isoformat())

    def test_detect_changes_when_maghrib_changed_return_none(self):
        changes = detect_changes(
            old_data={
                "masjids": {"m1": self.base_masjid, "m2": self.base_masjid}
            },
            new_data={
                "masjids": {"m1": self.masjid_with_maghrib_changed, "m2": self.base_masjid}
            })
        self.assertIsNone(changes)

    def test_detect_changes_when_jumas_changed_return_one_change(self):
        changes = detect_changes(
            old_data={
                "masjids": {"m1": self.base_masjid, "m2": self.base_masjid}
            },
            new_data={
                "masjids": {"m1": self.masjid_with_jumas_changed, "m2": self.base_masjid}
            })
        self.assertEqual(len(changes), 1)
        self.assertIn("m1", changes)
        self.assertEqual(changes["m1"].get("jumas_changed"), True)
        self.assertIsNotNone(changes["m1"].get("last_updated"))

    def test_detect_changes_when_fajr_and_maghrib_changed_return_one_change(self):
        changes = detect_changes(
            old_data={
                "masjids": {"m1": self.base_masjid, "m2": self.base_masjid}
            },
            new_data={
                "masjids": {"m1": self.masjid_with_fajr_and_magrib_changed, "m2": self.base_masjid}
            })
        self.assertEqual(len(changes), 1)
        self.assertIn("m1", changes)
        self.assertEqual(changes["m1"]["iqamas"]["fajr"].get("changed"), True)
        self.assertEqual(changes["m1"]["iqamas"]["maghrib"].get("changed"), True)
        self.assertIsNotNone(changes["m1"].get("last_updated"))

    def test_detect_changes_when_no_old_fajr_return_one_change(self):
        changes = detect_changes(
            old_data={
                "masjids": {"m1": self.masjid_with_no_fajr, "m2": self.base_masjid}
            },
            new_data={
                "masjids": {"m1": self.base_masjid, "m2": self.base_masjid}
            })
        self.assertEqual(len(changes), 1)
        self.assertIn("m1", changes)
        self.assertEqual(changes["m1"]["iqamas"]["fajr"].get("changed"), True)
        self.assertIsNotNone(changes["m1"].get("last_updated"))

    def test_detect_changes_when_no_new_iqamas_copy_old_values_and_return_none(self):
        changes = detect_changes(
            old_data={
                "masjids": {"m1": self.base_masjid, "m2": self.base_masjid}
            },
            new_data={
                "masjids": {"m1": self.masjid_with_no_iqamas, "m2": self.base_masjid}
            },
            save_to_file=self.test_saved_file)
        self.assertIsNone(changes)
        saved_data = read_json(self.test_saved_file)
        self.assertEqual(saved_data["masjids"]["m1"]["iqamas"], self.base_masjid["iqamas"])
        self.assertEqual(saved_data["masjids"]["m1"]["jumas"], self.base_masjid["jumas"])
        self.assertEqual(saved_data["masjids"]["m1"].get("last_updated"), self.base_masjid["last_updated"])

    @patch('handler.datetime')
    def test_detect_changes_when_new_masjid_return_one_change(self, datetime_mock):
        datetime_mock.datetime.utcnow.return_value = self.mocked_now
        changes = detect_changes(
            old_data={
                "masjids": {"m1": self.base_masjid}
            },
            new_data={
                "masjids": {"m2": self.base_masjid}
            },
            save_to_file=self.test_saved_file)
        self.assertEqual(len(changes), 1)
        self.assertIn("m2", changes)
        saved_data = read_json(self.test_saved_file)
        self.assertEqual(saved_data["masjids"]["m2"].get("last_updated"), self.mocked_now.isoformat())

    def test_detect_changes_when_no_change_copy_changed_on_from_old_data(self):
        changes = detect_changes(
            old_data={
                "masjids": {"m1": self.masjid_with_changed_on}
            },
            new_data={
                "masjids": {"m1": self.base_masjid}
            },
            save_to_file=self.test_saved_file)
        self.assertIsNone(changes)
        saved_data = read_json(self.test_saved_file)
        self.assertEqual(saved_data["masjids"]["m1"]["iqamas"]["fajr"].get("changed_on"), self.masjid_with_changed_on["iqamas"]["fajr"]["changed_on"])

    @patch('handler.datetime')
    def test_detect_changes_when_fajr_changed_set_changed_on_today(self, datetime_mock):
        datetime_mock.datetime.utcnow.return_value = self.mocked_now
        changes = detect_changes(
            old_data={
                "masjids": {"m1": self.base_masjid}
            },
            new_data={
                "masjids": {"m1": self.masjid_with_fajr_changed}
            },
            save_to_file=self.test_saved_file)
        self.assertIsNotNone(changes)
        saved_data = read_json(self.test_saved_file)
        self.assertEqual(saved_data["masjids"]["m1"]["iqamas"]["fajr"].get("changed_on"), self.mocked_now.date().isoformat())
