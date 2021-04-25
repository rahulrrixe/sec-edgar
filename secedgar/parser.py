import json
import logging
import os
import re
import uu

from secedgar.utils import make_path


class MetaParser:
    """Utility class to extract metadata and documents from a single text file.

    .. warning::
        The ``MetaParser`` class is still experimental. Use with caution.

    .. versionadded:: 0.3.0
    """

    def __init__(self):

        self.re_doc = re.compile("<DOCUMENT>(.*?)</DOCUMENT>", flags=re.DOTALL)
        self.re_sec_doc = re.compile("<SEC-DOCUMENT>(.*?)</SEC-DOCUMENT>", flags=re.DOTALL)
        self.re_text = re.compile("<TEXT>(.*?)</TEXT>", flags=re.DOTALL)
        self.re_sec_header = re.compile("<SEC-HEADER>.*?\n(.*?)</SEC-HEADER>", flags=re.DOTALL)

    def process(self, infile, out_dir=None, create_subdir=True, rm_infile=False):
        """Process a text file and save processed files.

        Args:
            infile (str): Full path to a text file.
            out_dir (str): Directory to store output files. Defaults to the parent directory of
                infile.
            create_subdir (bool): If a subdirectory with the name of the infile should be created.
                If this is not true, files will be prefixed with the infile filename.
            rm_infile (bool): If the infile should be removed after processing. Defaults to False.

        Returns:
            None
        """
        if not infile.endswith('.txt'):
            raise ValueError('{file} Does not appear to be a .txt file.'.format(file=infile))

        with open(infile, encoding="utf8") as f:
            intxt = f.read()

        if out_dir is None:
            out_dir = os.path.dirname(infile)
        infile_base = os.path.basename(infile).split('.txt')[0]
        metadata_file_format = "{base}_{num}.metadata.json"
        document_file_format = '{base}_{sec_doc_num}.{file}'
        if create_subdir:
            out_dir = os.path.join(out_dir, infile_base)
            make_path(out_dir)
            metadata_file_format = "{num}.metadata.json"
            document_file_format = '{sec_doc_num}.{file}'
        sec_doc_cursor = 0
        sec_doc_count = intxt.count("<SEC-DOCUMENT>")
        for sec_doc_num in range(sec_doc_count):
            sec_doc_match = self.re_sec_doc.search(intxt, pos=sec_doc_cursor)
            if not sec_doc_match:
                break

            sec_doc_cursor = sec_doc_match.span()[1]
            sec_doc = sec_doc_match.group(1)

            # metadata
            metadata_match = self.re_sec_header.search(sec_doc)
            metadata_txt = metadata_match.group(1)
            metadata_cursor = metadata_match.span()[1]
            metadata_filename = metadata_file_format.format(base=infile_base, num=sec_doc_num)
            metadata_file = os.path.join(out_dir, metadata_filename)
            metadata_dict = self.process_metadata(metadata_txt)
            # logging.info("Metadata written into {}".format(metadata_file))

            # Loop through every document
            metadata_dict["documents"] = []
            documents = sec_doc[metadata_cursor:].strip()
            doc_count = documents.count("<DOCUMENT>")
            doc_cursor = 0
            for doc_num in range(doc_count):
                doc_match = self.re_doc.search(documents, pos=doc_cursor)
                if not sec_doc_match:
                    break
                doc = doc_match.group(1)
                doc_cursor = doc_match.span()[1]
                doc_metadata = self.process_document_metadata(doc)
                metadata_dict["documents"].append(doc_metadata)

                # Get file data and file name
                doc_filename = doc_metadata["filename"]
                doc_txt = self.re_text.search(doc).group(1).strip()
                target_doc_filename = document_file_format.format(
                    base=infile_base,
                    sec_doc_num=sec_doc_num,
                    file=doc_filename
                )
                doc_outfile = os.path.join(out_dir, target_doc_filename)

                is_uuencoded = doc_txt.find("begin 644 ") != -1

                if is_uuencoded:
                    logging.info("{} contains an uu-encoded file".format(infile))
                    encfn = doc_outfile + ".uu"
                    with open(encfn, "w", encoding="utf8") as encfh:
                        encfh.write(doc_txt)
                    uu.decode(encfn, doc_outfile)
                    os.remove(encfn)
                else:
                    logging.info("{} contains an non uu-encoded file".format(infile))
                    with open(doc_outfile, "w", encoding="utf8") as outfh:
                        outfh.write(doc_txt)

            # Save SEC-DOCUMENT metadata to file
            with open(metadata_file, "w", encoding="utf8") as fileh:
                formatted_metadata = json.dumps(metadata_dict, indent=2,
                                                sort_keys=True, ensure_ascii=False)
                fileh.write(formatted_metadata)

        if rm_infile:
            os.remove(infile)

    @staticmethod
    def process_metadata(curr_doc):
        """Process the metadata of the focal document.

        Args:
            curr_doc (str): Process meta data for single focal document.

        Return:
            out_dict (dict): Meta data from focal document.
        """
        out_dict = {}
        levels = [None, None]

        for line in curr_doc.split("\n"):

            logging.debug("Line: '{}'".format(line))

            if "<ACCEPTANCE-DATETIME>" in line:
                out_dict["acceptance-datetime"] = \
                    line[len("<ACCEPTANCE-DATETIME>"):]
                continue

            if "<DESCRIPTION>" in line:
                out_dict["description"] = line[len("<DESCRIPTION>"):]
                continue

            # e.g. "CONFORMED SUBMISSION TYPE:	8-K"
            # *+ -> possessive quantifier
            m = re.match(r"^(\w.*):\t*([^\t]+)$", line)
            if m:
                logging.debug("Match A:B")
                out_dict[m.group(1).replace(" ", "_")] = m.group(2)
                continue

            # Level 1 header
            # Headers have 1 initial tab less than data
            m = re.match("^(?!\t)(.+):\t*$", line)
            if m:
                levels[0] = m.group(1).replace(" ", "_")
                levels[1] = None
                if levels[0] not in out_dict:
                    out_dict[levels[0]] = dict()
                    logging.debug("Creating level 1 header {}"
                                  .format(levels[0]))
                continue

            # Level 2 header (must be before the data for correct matching)
            # In fact "level 1 data" match this too
            m = re.match("^\t(.+):\t*$", line)
            if m:
                levels[1] = m.group(1).replace(" ", "_")
                if levels[1] not in out_dict[levels[0]]:
                    out_dict[levels[0]][levels[1]] = {}
                    logging.debug("Creating level 2 header {}"
                                  .format(levels[1]))
                continue

            # Level 1 data
            m = re.match("^\t(?!\t)(.+):\t*(.+)$", line)
            if m:
                out_dict[levels[0]][m.group(1)] = m.group(2)
                logging.debug("Level 1 data. Levels[0]={}; group={}"
                              .format(levels[0], m.group(1)))
                continue

            # Level 2 data
            m = re.match("^\t\t(.+):\t*(.+)$", line)
            if m:
                logging.debug("Level 2 data")
                key = m.group(1).replace(" ", "_")
                out_dict[levels[0]][levels[1]][key] = m.group(2)
                continue

        return out_dict

    @staticmethod
    def process_document_metadata(doc):
        """Process the metadata of an embedded document.

        Args:
            doc (str): Document to extract meta data from.

        Return:
            dict: Dictionary with fields parsed from document.
        """
        metadata_doc = {}

        # Document type
        type_m = re.search("<TYPE>(.*?)\n", doc)
        if type_m:
            metadata_doc["type"] = type_m.group(1)

        # Document sequence
        seq_m = re.search("<SEQUENCE>(.*?)\n", doc)
        if seq_m:
            metadata_doc["sequence"] = seq_m.group(1)

        # Document filename
        fn_m = re.search("<FILENAME>(.*?)\n", doc)
        metadata_doc["filename"] = fn_m.group(1)

        return metadata_doc
