import pytest
from secedgar.parser import MetaParser


class TestParser:
    parser = MetaParser()

    def test_process_document_metadata(self):
        doc = """<TYPE>10-K
        <SEQUENCE>123
        <FILENAME>test-filename.txt
        """
        metadata = self.parser.process_document_metadata(doc)
        assert metadata == {"type": "10-K", "sequence": "123", "filename": "test-filename.txt"}

    @pytest.mark.parametrize(
        "bad_filetype",
        [
            "xml",
            "json",
            "html",
            "txt.gz",
            "zip"
        ]
    )
    def test_bad_filetypes_raises_error(self, bad_filetype):
        with pytest.raises(ValueError):
            self.parser.process(infile="test.{0}".format(bad_filetype))
