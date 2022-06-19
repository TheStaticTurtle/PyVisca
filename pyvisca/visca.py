import socket
import struct

class ViscaObject:
	def __init__(self):
		pass

	def check(self, value):
		return False

	def read(self, value, context=None):
		if context is None:
			context = {}
		return None

	def write(self, context):
		return None

class ViscaFixedObject(ViscaObject):
	def __init__(self, value):
		super().__init__()
		self.value = value

	def __repr__(self):
		return f"ViscaFixedObject({hex(self.value)})"

	def check(self, value):
		return value == self.value

	def read(self, value, context=None):
		return value

	def write(self, context):
		return self.value

class ViscaMultiByteValueObject(ViscaObject):
	def __init__(self, count, index, var_name):
		super().__init__()
		self.count = count
		self.index = index
		self.var_name = var_name

	def check(self, value):
		return True

	def read(self, value, context=None):
		if context is None:
			context = {}
		if self.count == 1:
			context[self.var_name] = value
			return value

	def write(self, context):
		if self.count == 1:
			return context[self.var_name]
class ViscaMultiHalfByteValueObject(ViscaObject):
	def __init__(self, count, index, top_bits, var_name):
		super().__init__()
		self.count = count
		self.index = index
		self.top_bits = top_bits
		self.var_name = var_name

	def check(self, value):
		return (value & 0xf0) == self.top_bits

	def write(self, context):
		if self.count == 4:
			raw = struct.pack(">h", context[self.var_name])
			table = [raw[0] >> 4, raw[0] & 0xf, raw[1] >> 4, raw[1] & 0xf]
			return table[self.index]
		if self.count == 1:
			return context[self.var_name] + self.top_bits
		return None

	def read(self, value, context=None):
		if context is None:
			context = {}
		if self.count == 1:
			context[self.var_name] = value - self.top_bits
			return value - self.top_bits
		if self.count == 4:
			if self.var_name not in context:
				context[self.var_name] = [0, 0, 0, 0]
			context[self.var_name][self.index] = value
			if self.index == 3:
				msb = context[self.var_name][0] << 4 + context[self.var_name][1]
				lsb = context[self.var_name][2] << 4 + context[self.var_name][3]
				context[self.var_name] = struct.unpack(">h", bytes([msb, lsb]))[0]
				return context[self.var_name]
		return None


COMMANDS = {
	"CamPowerOn":  [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x0), ViscaFixedObject(0x02)],
	"CamPowerOff": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x0), ViscaFixedObject(0x03)],

	"CamZoomStop":         [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x07), ViscaFixedObject(0x0)],
	"CamZoomStandardTele": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x07), ViscaFixedObject(0x02)],
	"CamZoomStandardWide": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x07), ViscaFixedObject(0x03)],
	"CamZoomVariableTele": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x07), ViscaMultiHalfByteValueObject(1, 0, 0x20, 'speed')],
	"CamZoomVariableWide": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x07), ViscaMultiHalfByteValueObject(1, 0, 0x30, 'speed')],
	"CamZoomDirect":       [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x47), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'zoom_absolute'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'zoom_absolute'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'zoom_absolute'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'zoom_absolute')],

	"CamFocusStop":         [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x08), ViscaFixedObject(0x00)],
	"CamFocusStandardFar":  [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x08), ViscaFixedObject(0x02)],
	"CamFocusStandardNear": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x08), ViscaFixedObject(0x03)],
	"CamFocusVariableFar":  [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x08), ViscaMultiHalfByteValueObject(1, 0, 0x20, 'speed')],
	"CamFocusVariableNear": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x08), ViscaMultiHalfByteValueObject(1, 0, 0x30, 'speed')],
	"CamFocusDirect":       [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x48), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'focus_absolute'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'focus_absolute'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'focus_absolute'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'focus_absolute')],
	"CamFocusAFOn":         [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x38), ViscaFixedObject(0x02)],
	"CamFocusAFOff":        [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x38), ViscaFixedObject(0x03)],
	"CamFocusAFAutoManual": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x38), ViscaFixedObject(0x10)],
	"CamFocusLock":         [ViscaFixedObject(0x81), ViscaFixedObject(0x0a), ViscaFixedObject(0x04), ViscaFixedObject(0x68), ViscaFixedObject(0x02)],
	"CamFocusUnlock":       [ViscaFixedObject(0x81), ViscaFixedObject(0x0a), ViscaFixedObject(0x04), ViscaFixedObject(0x68), ViscaFixedObject(0x03)],

	"CamZoomFocusDirect":   [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x47), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'zoom_absolute'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'zoom_absolute'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'zoom_absolute'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'zoom_absolute'), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'focus_absolute'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'focus_absolute'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'focus_absolute'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'focus_absolute')],

	"PanTiltDriveUp":        [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x01), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaFixedObject(0x03), ViscaFixedObject(0x01)],
	"PanTiltDriveDown":      [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x01), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaFixedObject(0x03), ViscaFixedObject(0x02)],
	"PanTiltDriveLeft":      [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x01), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaFixedObject(0x01), ViscaFixedObject(0x03)],
	"PanTiltDriveRight":     [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x01), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaFixedObject(0x02), ViscaFixedObject(0x03)],
	"PanTiltDriveUpLeft":    [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x01), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaFixedObject(0x01), ViscaFixedObject(0x01)],
	"PanTiltDriveUpRight":   [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x01), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaFixedObject(0x02), ViscaFixedObject(0x01)],
	"PanTiltDriveDownLeft":  [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x01), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaFixedObject(0x01), ViscaFixedObject(0x02)],
	"PanTiltDriveDownRight": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x01), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaFixedObject(0x02), ViscaFixedObject(0x02)],
	"PanTiltDriveStop":      [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x01), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaFixedObject(0x03), ViscaFixedObject(0x03)],
	"PanTiltDriveAbsolute":  [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x02), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'pan_absolute'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'pan_absolute'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'pan_absolute'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'pan_absolute'), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'tilt_absolute'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'tilt_absolute'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'tilt_absolute'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'tilt_absolute')],
	"PanTiltDriveRelative":  [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x03), ViscaMultiByteValueObject(1, 0, 'pan_speed'), ViscaMultiByteValueObject(1, 0, 'tilt_speed'), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'pan_relative'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'pan_relative'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'pan_relative'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'pan_relative'), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'tilt_relative'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'tilt_relative'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'tilt_relative'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'tilt_relative')],
	"PanTiltDriveHome":      [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x04)],
	"PanTiltDriveReset":     [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x06), ViscaFixedObject(0x05)],

	"CamWhiteBalanceAuto":             [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x35), ViscaFixedObject(0x00)],
	"CamWhiteBalanceIndoorMode":       [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x35), ViscaFixedObject(0x01)],
	"CamWhiteBalanceOutdoorMode":      [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x35), ViscaFixedObject(0x02)],
	"CamWhiteBalanceOnepushMode":      [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x35), ViscaFixedObject(0x03)],
	"CamWhiteBalanceManual":           [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x35), ViscaFixedObject(0x05)],
	"CamWhiteBalanceColorTemperature": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x35), ViscaFixedObject(0x20)],
	"CamWhiteBalanceOnepushTrigger":   [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x10), ViscaFixedObject(0x05)],

	"CamRedGainReset":  [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x03), ViscaFixedObject(0x00)],
	"CamRedGainUp":     [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x03), ViscaFixedObject(0x02)],
	"CamRedGainDown":   [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x03), ViscaFixedObject(0x03)],
	"CamRedGainDirect": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x43), ViscaFixedObject(0x00), ViscaFixedObject(0x00), ViscaMultiHalfByteValueObject(2, 0, 0x00, 'direct'), ViscaMultiHalfByteValueObject(2, 1, 0x00, 'direct')],

	"CamBlueGainReset":  [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x04), ViscaFixedObject(0x00)],
	"CamBlueGainUp":     [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x04), ViscaFixedObject(0x02)],
	"CamBlueGainDown":   [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x04), ViscaFixedObject(0x03)],
	"CamBlueGainDirect": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x44), ViscaFixedObject(0x00), ViscaFixedObject(0x00), ViscaMultiHalfByteValueObject(2, 0, 0x00, 'direct'), ViscaMultiHalfByteValueObject(2, 1, 0x00, 'direct')],

	"CamColorTempReset":  [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x20), ViscaFixedObject(0x00)],
	"CamColorTempUp":     [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x20), ViscaFixedObject(0x02)],
	"CamColorTempDown":   [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x20), ViscaFixedObject(0x03)],
	"CamColorTempDirect": [ViscaFixedObject(0x81), ViscaFixedObject(0x01), ViscaFixedObject(0x04), ViscaFixedObject(0x20), ViscaMultiHalfByteValueObject(2, 0, 0x00, 'direct'), ViscaMultiHalfByteValueObject(2, 1, 0x00, 'direct')],

	"CamPanTiltPositionInquery": [ViscaFixedObject(0x81), ViscaFixedObject(0x09), ViscaFixedObject(0x06), ViscaFixedObject(0x12)],
	"CamPanTiltPositionInqueryResponse": [ViscaFixedObject(0x90), ViscaFixedObject(0x50), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'pan_absolute'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'pan_absolute'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'pan_absolute'), ViscaMultiHalfByteValueObject(4 ,3, 0x00, 'pan_absolute'), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'tilt_absolute'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'tilt_absolute'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'tilt_absolute'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'tilt_absolute')],

	"CamZoomPositionInquery": [ViscaFixedObject(0x81), ViscaFixedObject(0x09), ViscaFixedObject(0x04), ViscaFixedObject(0x47)],
	"CamZoomPositionInqueryResponse": [ViscaFixedObject(0x90), ViscaFixedObject(0x50), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'zoom'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'zoom'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'zoom'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'zoom')],

	"CamFocusPositionInquery": [ViscaFixedObject(0x81), ViscaFixedObject(0x09), ViscaFixedObject(0x04), ViscaFixedObject(0x48)],
	"CamFocusPositionInqueryResponse": [ViscaFixedObject(0x90), ViscaFixedObject(0x50), ViscaMultiHalfByteValueObject(4, 0, 0x00, 'zoom'), ViscaMultiHalfByteValueObject(4, 1, 0x00, 'zoom'), ViscaMultiHalfByteValueObject(4, 2, 0x00, 'zoom'), ViscaMultiHalfByteValueObject(4, 3, 0x00, 'zoom')],

	"CamTallyNone":    [ViscaFixedObject(0x81), ViscaFixedObject(0xa), ViscaFixedObject(0x02), ViscaFixedObject(0x02), ViscaFixedObject(0x03)],
	"CamTallyPreview": [ViscaFixedObject(0x81), ViscaFixedObject(0xa), ViscaFixedObject(0x02), ViscaFixedObject(0x02), ViscaFixedObject(0x01)],
	"CamTallyLive":    [ViscaFixedObject(0x81), ViscaFixedObject(0xa), ViscaFixedObject(0x02), ViscaFixedObject(0x02), ViscaFixedObject(0x02)],
}

class Visca:

	def parse(self, data):
		decoded = None
		for command_name, command_parts in COMMANDS.items():
			if len(command_parts) + 1 != len(data):
				continue
			context = {}
			valid_command = True
			for i, command_part in enumerate(command_parts):
				if not command_part.check(data[i]):
					valid_command = False
					break
			if valid_command:
				for i, command_part in enumerate(command_parts):
					command_part.read(data[i], context=context)
				decoded = (command_name, context)

		return decoded

	def build(self, command, context):
		parts = COMMANDS[command]
		buf = b""

		for part in parts:
			buf += bytes([part.write(context)])

		buf += b"\xff"

		return buf