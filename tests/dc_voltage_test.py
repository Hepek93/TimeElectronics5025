from te5025 import TE5025

# Initialize the calibrator (Update address to match your GPIB info)
cal = TE5025('GPIB0::25::INSTR')

cal.set_voltage_dc(range='20V', amplitude=10.0)
cal.output_enable()
