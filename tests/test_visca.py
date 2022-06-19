import unittest
from pyvisca import Visca

class MyTestCase(unittest.TestCase):
	def test_build_all_fixed(self):
		visca = Visca()
		result = visca.build("CamPowerOn", {})
		self.assertEqual(result, b"\x81\x01\x04\x00\x02\xff")

	def test_build_one_half_byte(self):
		visca = Visca()
		result = visca.build("CamZoomVariableTele", {"speed":5})
		self.assertEqual(result, b"\x81\x01\x04\x07\x25\xff")

	def test_build_four_half_byte(self):
		visca = Visca()
		result = visca.build("CamZoomDirect", {"zoom_absolute":-16384})
		self.assertEqual(result, b"\x81\x01\x04\x47\x0c\x00\x00\x00\xff")

	def test_build_two_byte(self):
		visca = Visca()
		result = visca.build("PanTiltDriveUp", {"tilt_speed":10, "pan_speed":10})
		self.assertEqual(result, b"\x81\x01\x06\x01\x0a\x0a\x03\x01\xff")



	def test_parse_all_fixed(self):
		visca = Visca()
		result = visca.parse(b"\x81\x01\x04\x00\x02\xff")
		self.assertEqual(result[0], "CamPowerOn")
		self.assertEqual(result[1], {})

	def test_parse_one_half(self):
		visca = Visca()
		result = visca.parse(b"\x81\x01\x04\x07\x25\xff")
		self.assertEqual(result[0], "CamZoomVariableTele")
		self.assertEqual(result[1], {"speed": 5})

	def test_parse_four_half(self):
		visca = Visca()
		result = visca.parse(b"\x81\x01\x04\x47\x0c\x00\x00\x00\xff")
		self.assertEqual(result[0], "CamZoomDirect")
		self.assertEqual(result[1], {"zoom_absolute":-16384})

	def test_parse_two_byte(self):
		visca = Visca()
		result = visca.parse(b"\x81\x01\x06\x01\x0a\x0a\x03\x01\xff")
		self.assertEqual(result[0], "PanTiltDriveUp")
		self.assertEqual(result[1], {"tilt_speed":10, "pan_speed":10})



if __name__ == '__main__':
	unittest.main()
