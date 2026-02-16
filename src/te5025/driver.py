import pyvisa
import time

class TE5025:
    """Class that controls Time Electronics 5025.
    """
    
    def __init__(self, dev_info, read_termination = '\r\n', write_termination = '\r\n', delay = 0.05, timeout = 10_000) -> None:
        """Constructor

        Args:
            dev_info (str): GPIB connection e.g. ['GPIB0::25::INSTR'])
            read_termination (str, optional): Read termination. Defaults to '\\r\\n'.
            write_termination (str, optional): Write termination. Defaults to '\\r\\n'.
            delay (float, optional): Delay between two commands. Defaults to 0.05.
            timeout (int, optional): VISA timeout. Defaults to 10_000.
        """
        self.__instrument_connected = False
        
        rm = pyvisa.ResourceManager()
        try:
            self.__inst = rm.open_resource(dev_info, write_termination=write_termination, read_termination=read_termination)
            self.__instrument_connected = True
            self.__inst.timeout = timeout
            self.__delay = delay
        except:
            print('Check connection with Time Electronics 5025')
    
    def __get_data(self,query) -> str:
        if self.__instrument_connected:
            try:
                recv = self.__inst.query(query)
                time.sleep(self.__delay)
                return recv
            except:
                print('Can not query data from the calibrator')
            
        else:
            print('Time Electronics 5025 is not connected')
        return None

    def __write_data(self, data) -> bool:
        if self.__instrument_connected:
            try:
                self.__inst.write(data)
                time.sleep(self.__delay)
                return True
            except Exception as e: 
                print('Can not send data to the Time Electronics 5025')
                print('Reason:', e)
            
        else:
            print('Time Electronics 5025 is not connected')
        return False

    def close_connection(self) -> None:
        """Close connection
        """
        if self.__instrument_connected:
            self.__inst.close()
            self.__instrument_connected = False

    def get_info(self) -> str:
        """Get calibrator info

        Returns:
            str: info
        """
        return self.__get_data('*IDN?')
    
    def clear_error(self) -> bool:
        """Clear remote error buffer.

        Returns:
            bool: status
        """
        return self.__write_data('*CLS')
    
    def get_error(self) -> str:
        """Get next error from error buffer

        Returns:
            str: error
        """

        return self.__get_data('SYST:ERR?')

    def get_error_count(self) -> str:
        """Get error count in error buffer

        Returns:
            str: error count
        """

        return self.__get_data('SYST:ERR:COUN?')
    
    def set_remote(self) -> bool:
        """Puts the calibrator in remote mode

        Returns:
            bool: status
        """

        return self.__write_data('SYST:REM')
    
    def set_local(self) -> bool:
        """Puts the calibrator in local mode

        Returns:
            bool: status
        """

        return self.__write_data('SYST:LOC')
    
    def get_internal_temperature(self) -> str:
        """Get internal temperature of calibrator

        Returns:
            str: temperature in degrees Celsius
        """
        self.__write_data('unit:temp c')
        return self.__get_data('syst:mod:vs:temp?')

    def set_voltage_dc(self, range, amplitude) -> bool:
        """Set Voltage DC range and amplitude

        Args:
            range (int, float, str): Range may be 20mV, 200mV, 2V, 20V, 200V, 1kV
            amplitude (int, float, str): Amplitude may be in range [0.02 V, 1050 V] 

        Returns:
            bool: status
        """
        ret3 = self.__write_data('FUNC DC')
        ret1 = self.set_voltage_range(range)
        ret2 = self.set_voltage_amplitude(amplitude)

        return ret1 and ret2 and ret3
    
    def set_voltage_range(self, range) -> bool:
        """Set Voltage range

        Args:
            range (int, str): Range may be 20mV, 200mV, 2V, 20V, 200V, 1kV

        Returns:
            bool: status
        """
        if not range in ['20mV','200mV','2V','20V','200V','1kV',0.02,0.2,2,20,200,1000]:
            return False 
        else:
            return self.__write_data(f'VOLT:RANG {range}')

    def set_voltage_amplitude(self, amplitude) -> bool:
        """Set Voltage amplitude

        Args:
            amplitude (int, float, str): Amplitude may be in range [0 V, 1050 V] 

        Returns:
            bool: status
        """
        try:
            amplitude = float(amplitude)
            if amplitude >= -1050 and amplitude<=1050:
                if amplitude <= float(self.get_voltage_range())*1.1:
                    return self.__write_data(f'VOLT:AMPL {amplitude}')
                else:
                    return False
            else:
                return False
        except:
            return False

    def get_voltage_range(self) -> str:
        """Get Voltage range

        Returns:
            str: range
        """
        return self.__get_data('VOLT:RANG?')

    def get_voltage_amplitude(self) -> str:
        """Get Voltage amplitude

        Returns:
            str: amplitude
        """

        return self.__get_data('VOLT:AMPL?')

    def set_current_dc(self, range, amplitude) -> bool:
        """Set Current DC range and amplitude

        Args:
            range (int, float, str): Range may be 200uA, 2mA, 20mA, 200mA, 2A, 20A 
            amplitude (int, float, str): Amplitude may be in range [0 A, 22 A] 

        Returns:
            bool: status
        """
        ret3 = self.__write_data('FUNC DC')
        ret1 = self.set_current_range(range)
        ret2 = self.set_current_amplitude(amplitude)

        return ret1 and ret2 and ret3


    def set_current_range(self, range) -> bool:
        """Set Current range

        Args:
            range (int,str): Range may be 200uA, 2mA, 20mA, 200mA, 2A, 20A

        Returns:
            bool: status
        """
        if not range in ['200uA','2mA','20mA','200mA','2A','20A',2E-4,2E-3,0.02,0.2,2,20]:
            return False 
        else:
            return self.__write_data(f'CURR:RANG {range}')


    def set_current_amplitude(self, amplitude) -> bool:
        """Set Current amplitude

        Args:
            amplitude (int, float, str): Amplitude may be in range [0 A, 22 A]

        Returns:
            bool: status
        """

        try:
            amplitude = float(amplitude)
            if amplitude >= -22 and amplitude<=22:
                if amplitude <= float(self.get_current_range())*1.1:
                    return self.__write_data(f'CURR:AMPL {amplitude}')
                else:
                    return False
            else:
                return False
        except:
            return False

    def get_current_range(self) -> str:
        """Get Current DC range

        Returns:
            str: range
        """
        return self.__get_data('CURR:RANG?')

    
    def get_current_amplitude(self) -> str:
        """Get Current DC amplitude

        Returns:
            str: amplitude
        """
        return self.__get_data('CURR:AMPL?')

    def set_voltage_ac(self, range, amplitude, frequency) -> bool:
        """Set Voltage AC range and amplitude

        Args:
            range (int,float,str): Range may be 20mV, 200mV, 2V, 20V, 200V, 1kV 
            amplitude (int,float,str): Amplitude may be in range [0.02 V, 1050 V] 
            frequency (int,str): Frequency may be in range [0,20 kHz] 

        Returns:
            bool: status
        """
        ret3 = self.__write_data('FUNC SIN')
        ret4 = self.set_acv_frequency(frequency)
        ret1 = self.set_voltage_range(range)
        ret2 = self.set_voltage_amplitude(amplitude)

        return ret1 and ret2 and ret3 and ret4

    def set_current_ac(self, range, amplitude, frequency) -> bool:
        """Set Current DC range and amplitude

        Args:
            range (int,float,str): Range may be 200uA, 2mA, 20mA, 200mA, 2A, 20A 
            amplitude (int,float,str): Amplitude may be in range [0 A, 22 A]  
            frequency (int,str): Frequency may be in range [0,20 kHz] 

        Returns:
            bool: status
        """

        ret3 = self.__write_data('FUNC SIN')
        ret4 = self.set_acv_frequency(frequency)
        ret1 = self.set_current_range(range)
        ret2 = self.set_current_amplitude(amplitude)
        return ret1 and ret2 and ret3 and ret4

    def set_acv_frequency(self, frequency) -> bool:
        """Set AC Voltage/Current frequency.

        Args:
            frequency (int,str): _description_

        Returns:
            bool: status
        """

        try:
            frequency = int(frequency)
            if frequency > 0 and frequency <= 20000:
                return self.__write_data(f'FREQ {frequency}')
        except:
            return False
        
    def get_acv_frequency(self) -> str:
        """Get AC Voltage/Current frequency

        Returns:
            str: frequency
        """
        return self.__get_data('FREQ?')
    
    def set_fixed_resistance(self, resistance) -> bool:
        """Set fixed resistance.

        Args:
            resistance (int, str): Resistance may be 0, 1, 10, 100, 1000, 1E4, 1E5, 1E6, 1E7, 1E8 or 1E9.

        Returns:
            bool: status
        """
        
        if resistance in [0, 1, 10, 100, 1000, 1E4, 1E5, 1E6, 1E7, 1E8, 1E9,
                          '0r','1r','10r','100r','1kr','10kr','100kr','1mr','10mr','100mr','1gr']:
            return self.__write_data(f'RES {resistance}')
        else:
            return False
        
    def get_fixed_resistance(self) -> str:
        """Get fixed resistor value.

        Returns:
            str: resistance
        """
        return self.__get_data('RES?')
    
    def set_arbitrary_resistance(self, resistance) -> bool:
        """Set arbitrary resistance.

        Args:
            resistance (int, str): Resistance may be in range [0r, 40mr]

        Returns:
            bool: status
        """
        return self.__write_data(f'SRES {resistance}')
        
    def get_arbitrary_resistance(self) -> str:
        """Get arbitrary resistor value.

        Returns:
            str: resistance
        """

        return self.__get_data('SRES?')

    def set_capacitance(self, capacitance) -> bool:
        """Set fixed capacitance.

        Args:
            capacitance (int, str): Capacitance may be 1nf, 10nf, 100nf, 1uf, 10uf, 100uf.

        Returns:
            bool: status
        """
        if capacitance in [1E-9, 1E-8, 1E-7, 1E-6, 1E-5, 1E-4,
                          '1nf','10nf','100nf','1uf','10uf','100uf']:
            return self.__write_data(f'CAP {capacitance}')
        else:
            return False

    def get_capacitance(self) -> str:
        """Get fixed capacitor value.

        Returns:
            str: capacitance
        """

        return self.__get_data('CAP?')

    def set_inductance(self, inductance) -> bool:
        """Set fixed inductance.

        Args:
            inductance (int, str): Inductance may be 1mh, 1.9mh, 5mh, 10mh, 19mh, 50mh, 100mh, 190mh, 500mh, 1h or 10h.

        Returns:
            bool: status
        """

        if inductance in [1E-3, 1.9E-3, 5e-3, 10E-3, 19E-3, 5E-2, 0.1, 0.19, 0.5, 1, 10,
                          '1mh','1.9mh','5mh','10mh','19mh','50mh','100mh','190mh','500mh','1h','10h']:
            return self.__write_data(f'IND {inductance}')
        else:
            return False

    def get_inductance(self) -> str:
        """Get fixed inductance value.

        Returns:
            str: inductance
        """

        return self.__get_data('IND?')

    def set_conductance(self, conductance) -> bool:
        """Set fixed conductance.

        Args:
            conductance (int, str): Conductance may be 1ns, 10ns, 100ns, 1us, 10us, 100us, 1ms, 10ms, 100ms, 1s.

        Returns:
            bool: status
        """

        if conductance in [1E-9, 1E-8, 1E-7, 1E-6, 1E-5, 1E-4, 1E-3, 1E-2, 0.1, 1, 
                          '1ns','10ns','100ns','1us','10us','100us','1ms','10ms','100ms','1s']:
            return self.__write_data(f'COND {conductance}')
        else:
            return False

    def get_conductance(self) -> str:
        """Get fixed conductance value.

        Returns:
            str: conductance
        """ 

        return self.__get_data('COND?')

    def set_RTD_temperature(self, temperature, unit="C") -> bool:
        """Simulate resistance of RTD(PT100).

        Args:
            temperature (float,str): Temperature can be any temperature in range [-180, 850] in Celsius, [93.15,1123.15] in Kelvins and [-292,1562] in Farenheits.
            unit (str, optional): C - Celsius, K - Kelvin, F - Farenheit. Defaults to "C".

        Returns:
            bool: status
        """
        try:
            if unit.upper() == 'C' and  temperature >= -180 and temperature <= 850:
                return self.__write_data(f'RTD {temperature}C')
            elif unit.upper() == 'K' and  temperature >= 93.15 and temperature <= 1123.15:
                return self.__write_data(f'RTD {temperature}K')
            elif unit.upper() == 'F' and  temperature >= -292 and temperature <= 1562:
                return self.__write_data(f'RTD {temperature}F')
            else:
                return False
        except:
            return False

    def get_RTD_temperature(self) -> str:
        """Get temperature of simulated RTD (PT100)

        Returns:
            str: temperature
        """

        return self.__get_data('RTD?')

    def output_enable(self) -> bool:
        """Enable calibrator output

        Returns:
            bool: status
        """

        return self.__write_data('OUTP ON')

    def output_disable(self) -> bool:
        """Disable calibrator output.

        Returns:
            bool: status
        """
        return self.__write_data('OUTP OFF')


    def get_output_status(self) -> str:
        """Return calibrator output status.

        Returns:
            str: status
        """
        return self.__write_data('OUTP?')

    def set_TC_type(self, type = 'K') -> bool:
        """Select the thermocouple simulation type.

        Args:
            type (str, optional): B, E, J, K, N, R, S or T. Defaults to 'K'.

        Returns:
            bool: status
        """
        try:
            if type.upper() in ['B', 'E', 'J', 'K', 'N', 'R', 'S', 'T']:
                return self.__write_data(f'ther:type {type}')
            else:
                return False
        except:
            return False

    def get_TC_type(self) -> str:
        """Get selected the thermocouple simulation type.

        Returns:
            str: thermocouple type
        """

        return self.__get_data('ther:type?')

    def set_TC_temperature(self, temperature) -> bool:
        """Select the thermocouple simulated temperature.

        Args:
            temperature (str, int, float): Temperature to be simulated.

        Returns:
            bool: status
        """
        try:
            temperature = float(temperature)
            type = self.get_TC_type().upper()
            
            if type == 'J' and temperature >= -210 and temperature <= 1200:
                return self.__write_data(f'ther {temperature}')
            elif type == 'K' and temperature >= -200 and temperature <= 1250:
                return self.__write_data(f'ther {temperature}')
            elif type == 'T' and temperature >= -200 and temperature <= 400:
                return self.__write_data(f'ther {temperature}')
            elif type == 'R' and temperature >= -50 and temperature <= 1750:
                return self.__write_data(f'ther {temperature}')
            elif type == 'S' and temperature >= -50 and temperature <= 1750:
                return self.__write_data(f'ther {temperature}')
            elif type == 'B' and temperature >= 100 and temperature <= 1800:
                return self.__write_data(f'ther {temperature}')
            elif type == 'N' and temperature >= -200 and temperature <= 1300:
                return self.__write_data(f'ther {temperature}')
            elif type == 'E' and temperature >= -200 and temperature <= 1000:
                return self.__write_data(f'ther {temperature}')
            else:
                return False
        except:
            return False

    def get_TC_temperature(self) -> str:
        """Get the thermocouple simulated temperature.

        Returns:
            str: thermocouple temperature
        """

        return self.__get_data('ther?')

    def set_TC(self, temperature, type='K') -> bool:
        """Set the thermocouple temperature and type

        Args:
            temperature (str, float, int): Thermocouple temperature
            type (str, optional): Thermocouple type. Defaults to 'K'.

        Returns:
            bool: status
        """

        ret1 = self.set_TC_type(type)
        ret2 = self.set_TC_temperature(temperature)

        return ret1 and ret2

    def set_oscilloscope_frequency(self, frequency) -> bool:
        """Set oscilloscope frequency

        Args:
            frequency (str, int, float): Frequency can be 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500,
            1E3, 2E3, 5E3, 1E4, 2E4, 5E4, 1E5, 2E5, 5E5, 1E6, 2E6, 5E6, 1E7, 2E7, 5E7, 1E8.  

        Returns:
            bool: status
        """

        try:
            frequency = float(frequency)
            if frequency in [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1E3, 2E3, 5E3, 1E4, 2E4, 5E4, 1E5, 2E5, 5E5, 1E6, 2E6, 5E6, 1E7, 2E7, 5E7, 1E8]:
                self.__write_data(f'puls:sfr {frequency}')
        except:
            return False
        
    def get_oscilloscope_frequency(self) -> str:
            """Get oscilloscope frequency

            Returns:
                str: frequency
            """

            return self.__get_data('puls:sfr?')
    
    def set_oscilloscope_period(self, period) -> bool:
        """Set oscilloscope period

        Args:
            period (str, int, float): Period can be 10ns, 20ns, 50ns, 100ns, 200ns, 500ns, 1us, 2us, 5us, 10us, 20us, 50us,
            100us, 200us, 500us, 1ms, 2ms, 5ms, 10ms, 20ms, 50ms, 100ms, 200ms, 500ms, 1s, 2s, 5s, 10s.  

        Returns:
            bool: status
        """

        try:
            period = float(period)
            if period in [1E-8, 2E-8, 5E-8, 1E-7, 2E-7, 5E-7, 1E-6, 2E-6, 5E-6, 1E-5, 2E-5, 5E-5, 1E-4, 2E-4,
                              5E-4, 1E-3, 2E-3, 5E-3, 1E-2, 2E-2, 5E-2, 0.1, 0.2, 0.5, 1, 2, 5, 10]:
                self.__write_data(f'puls:sper {period}')
        except:
            return False
        
    def get_oscilloscope_period(self) -> str:
            """Get oscilloscope period

            Returns:
                str: period
            """

            return self.__get_data('puls:sper?')
    


    # def set_oscilloscope_duty_cycle(self, percentage=50) -> bool:
    #     """Set oscilloscope duty cycle. Note that frequency must be 100 Hz, 1 kHz or 10 kHz to use this option.

    #     Args:
    #         percentage (int, optional): Duty cycle percentage. Defaults to 50.

    #     Returns:
    #         bool: status
    #     """
    #     try:
    #         percentage = float(percentage)
    #         frequency = float(self.get_oscilloscope_frequency())
    #         if percentage >= 0 and percentage <= 100 and frequency in [100, 1000, 10000]:
    #             return self.__write_data(f'puls:dcycl {percentage}')
    #     except:
    #         return False
        
    # def get_oscilloscope_duty_cycle(self) -> str:
    #         """Get oscilloscope duty cycle

    #         Returns:
    #             str: percentage
    #         """

    #         return self.__get_data('puls:dcycl?')

    def set_ac_power(self, voltage, current, frequency=50, phase=0) -> bool:
        """Select the AC power function.

        Args:
            voltage (str, float, int):  Voltage can be any nubmer (0,1050], but range can be 0.02 V, 0.2 V, 2 V, 20 V, 200 V or 1000 V.
            current (str, int): Current can be any number (0,22], but range can be 2 A or 20 A.
            frequency (str, int, optional): Frequency can be in range [45 Hz, 400 Hz]. Defaults to 50.
            phase (str, float, int, optional): Phase can be in range [-90, 90]. Postive values of phase means the current
            is leading voltage, a negative value of phase means the current is lagging the voltage. Defaults to 0.

        Returns:
            bool: status
        """

        self.output_disable()

        try:
            voltage = float(voltage)
            current = float(current)
            frequency = float(frequency)
            phase = float(phase)
            volt_rang = 0
            if voltage <= 0.022:
                volt_rang = 0.02
            elif voltage <= 0.22:
                volt_rang = 0.2
            elif voltage <= 2.2:
                volt_rang = 2
            elif voltage <= 22:
                volt_rang = 20
            elif voltage <= 220:
                volt_rang = 200
            elif voltage <= 1050:
                volt_rang = 1000
            else:
                return False

            current_rang = 0
            if current <= 2.2:
                current_rang = 2
            elif current <= 22:
                current_rang = 20
            else:
                return False
            
            ret = self.__write_data(f'func sin')
            ret1 = self.__write_data(f'pow:rang {volt_rang},{current_rang}')
            ret2 = self.__write_data(f'pow {voltage},{current}')
            
            ret3 = self.__write_data(f'UNIT:PHAS DEG')
            if phase >= -90 and phase <= 90:
                ret4 = self.__write_data(f'pow:phase {phase}')
            else:
                return False
            
            if frequency >= 45 and frequency <= 400:
                ret5 = self.__write_data(f'freq {frequency}')
            else:
                return False

            return ret and ret1 and ret2 and ret3 and ret4 and ret5

        except:
            return False

    def get_ac_power(self, unit = 'WATT') -> str:
        """Get the AC power

        Args:
            unit (str, optional): Unit can be 'WATT' for watts or 'VA' for Volt Amperes. Defaults to 'W'.

        Returns:
            str: power
        """
        if self.__get_data('func?').upper() == 'SIN':
            if unit.upper() in ['WATT', 'VA']:
                self.__write_data(f'unit:pow {unit}')
                return self.__get_data('pow:pow?')
            else:
                return 'error'
        else:
            return 'error'

    def get_ac_power_parameters(self) -> str:
        """
        Get the AC power.

        Returns:
            str: voltage, current, frequency, phase
        """
        if self.__get_data('func?').upper() == 'SIN':
            v_a = self.__get_data('pow?')
            freq = self.__get_data('freq?')
            ph = self.__get_data('pow:phase?')

            return f'{v_a},{freq},{ph}'
        else:
            return 'error'

    def set_dc_power(self, voltage, current) -> bool:
        """Select the DC power function.

        Args:
            voltage (str, float, int):  Voltage can be any nubmer (0,1050], but range can be 0.02 V, 0.2 V, 2 V, 20 V, 200 V or 1000 V.
            current (str, int): Current can be any number (0,22], but range can be 2 A or 20 A.

        Returns:
            bool: status
        """

        self.output_disable()

        try:
            voltage = float(voltage)
            current = float(current)

            volt_rang = 0
            if voltage <= 0.022:
                volt_rang = 0.02
            elif voltage <= 0.22:
                volt_rang = 0.2
            elif voltage <= 2.2:
                volt_rang = 2
            elif voltage <= 22:
                volt_rang = 20
            elif voltage <= 220:
                volt_rang = 200
            elif voltage <= 1050:
                volt_rang = 1000
            else:
                return False

            current_rang = 0
            if current <= 2.2:
                current_rang = 2
            elif current <= 22:
                current_rang = 20
            else:
                return False
            
            ret = self.__write_data(f'func dc')
            ret1 = self.__write_data(f'pow:rang {volt_rang},{current_rang}')
            ret2 = self.__write_data(f'pow {voltage},{current}')

            return ret and ret1 and ret2

        except:
            return False

    def get_dc_power(self, unit = 'WATT') -> str:
        """Get the DC power

        Args:
            unit (str, optional): Unit can be 'WATT' for watts or 'VA' for Volt Amperes. Defaults to 'W'.

        Returns:
            str: power
        """
        if self.__get_data('func?').upper() == 'DC':
            if unit.upper() in ['WATT', 'VA']:
                self.__write_data(f'unit:pow {unit}')
                return self.__get_data('pow:pow?')
            else:
                return 'error'
        else:
            return 'error'

    def get_dc_power_parameters(self) -> str:
        """
        Get the DC power.
        
        Returns:
            str: voltage, current
        """
        if self.__get_data('func?').upper() == 'DC':
            return self.__get_data('pow?')
        else:
            return 'error'

    @staticmethod
    def list_instruments()->str:
        rm = pyvisa.ResourceManager()
        return rm.list_resources()
    
    