# coding:utf-8

import unittest2

from ..uploader import UploaderXML
from ..utils import read_config


class TestUploader(unittest2.TestCase):
    uploader = None

    @classmethod
    def setUpClass(cls):
        cfg = read_config()
        mysql = cfg["mysql"]
        cls.uploader = UploaderXML(log_lvl="debug", **mysql)

    # @unittest2.skip("Full")
    def test_upload(self):
        self.uploader.upload_archive()

    @unittest2.skip("Not full")
    def test_upload_csv(self):
        self.uploader.current_table = "addr_objects"
        self.uploader.update_table(["/srv/downloader_postal_code/tmp/part_0.csv"])
