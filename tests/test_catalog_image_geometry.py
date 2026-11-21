import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from catalog_image_geometry import native_image_dpi

class NativeImageGeometryTests(unittest.TestCase):
    def test_rotated_and_unrotated_photos_keep_the_same_native_resolution(self):
        normal={'width':300,'height':50,'transform':[144,0,0,24,0,0]}
        rotated={'width':50,'height':300,'transform':[0,24,-144,0,144,0]}
        self.assertAlmostEqual(native_image_dpi(normal),150)
        self.assertAlmostEqual(native_image_dpi(rotated),150)

    def test_degenerate_source_transform_is_rejected(self):
        with self.assertRaises(ValueError):
            native_image_dpi({'width':300,'height':50,'transform':[0,0,0,24,0,0]})
