import os
import struct
import tempfile
import unittest

import spinlab as sl


class rs2d_format_tester(unittest.TestCase):
    def test_import_minimal_rs2d_header_and_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            header_path = os.path.join(tmpdir, "header.xml")
            data_path = os.path.join(tmpdir, "data.dat")
            with open(header_path, "w", encoding="utf-8") as f:
                f.write(
                    """
<root>
  <params>
    <entry><key>ACQUISITION_MATRIX_DIMENSION_1D</key><value><value>1</value></value></entry>
    <entry><key>ACQUISITION_MATRIX_DIMENSION_2D</key><value><value>1</value></value></entry>
    <entry><key>ACQUISITION_MATRIX_DIMENSION_3D</key><value><value>1</value></value></entry>
    <entry><key>ACQUISITION_MATRIX_DIMENSION_4D</key><value><value>1</value></value></entry>
    <entry><key>RECEIVER_COUNT</key><value><value>1</value></value></entry>
    <entry><key>DWELL_TIME</key><value><value>0.5</value></value></entry>
  </params>
</root>
""".strip()
                )
            with open(data_path, "wb") as f:
                f.write(struct.pack(">2f", 1.0, 2.0))

            data = sl.io.formats.rs2d.import_rs2d(header_path)

            self.assertEqual(data.values.shape, ())
            self.assertEqual(data.values.item(), 2.0 + 1.0j)
            self.assertEqual(data.attrs["DWELL_TIME"], 0.5)


if __name__ == "__main__":
    unittest.main()
