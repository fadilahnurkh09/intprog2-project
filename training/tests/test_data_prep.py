import unittest
from PIL import Image
from training.prepare_faces import strict_face_crop,crop_then_resize
from training.prepare_glasses import center_crop_pair

class TestDataPrep(unittest.TestCase):
    def setUp(self):
        self.image=Image.new('RGB',(512,512),'white')
        self.mask=Image.new('L',(512,512),0)

    def test_strict_crop_keeps_original_pixels_and_size(self):
        c=strict_face_crop(self.image,(160,160,320,350))
        self.assertEqual(c.size,(224,224))
        self.assertEqual(c.getpixel((100,100)),(255,255,255))

    def test_strict_crop_rejects_big_face(self):
        with self.assertRaises(ValueError):
            strict_face_crop(self.image,(100,100,400,400))

    def test_roi_then_resize_is_explicit_alternative(self):
        self.assertEqual(crop_then_resize(self.image,(100,100,400,400)).size,(224,224))

    def test_pair_uses_same_center_rectangle(self):
        a,b=center_crop_pair(self.image,self.mask)
        self.assertEqual(a.size,(224,224))
        self.assertEqual(b.size,(224,224))

if __name__=='__main__':unittest.main()
