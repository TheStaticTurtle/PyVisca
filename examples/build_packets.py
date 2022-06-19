from pyvisca import Visca

visca = Visca()

power_on = visca.build("CamPowerOn", {})
print(power_on)

set_focus = visca.build("CamZoomFocusDirect", {"zoom_absolute": 0})
print(set_focus)