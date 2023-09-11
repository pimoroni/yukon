import tca
import time
from machine import ADC, Pin

"""
This is the program used to obtain calibration values for Yukon's voltage and current sensors.

Voltage In was measured with a multimeter parallel with the power input
+ ───────┬───────┐
        DMM    Yukon
g ───────┴───────┘

Voltage Out was measured with a multimeter connected to a proto module attached to Yukon
+ ─────┐   ┌─────┐
       Yukon    DMM
g ─────┘   └─────┘

Current was measured with a multimeter on the low side of the ground return path
+ ─────────┐   ┌─────┐
           Yukon    Load
g ───DMM───┘   └─────┘

A KeySight 34461A Digital Multimeter was used for measuring all voltages and currents up to 10A
For currents beyond 10A, the readout from the electronic load (a BK Precision 8601) was used,
with a -20mA offset applied to the constant current (as was needed for all currents 10A and below).
"""


CURRENT_SENSE_ADDR = 12      # 0b1100
TEMP_SENSE_ADDR = 13         # 0b1101
VOLTAGE_OUT_SENSE_ADDR = 14  # 0b1110
VOLTAGE_IN_SENSE_ADDR = 15   # 0b1111


# Main output enable
main_en = Pin.board.MAIN_EN
main_en.init(Pin.OUT, value=False)

# ADC mux enable pins
adc_mux_ens = (Pin.board.ADC_MUX_EN_1,
               Pin.board.ADC_MUX_EN_2)
adc_mux_ens[0].init(Pin.OUT, value=False)
adc_mux_ens[1].init(Pin.OUT, value=False)

# ADC mux address pins
adc_mux_addrs = (Pin.board.ADC_ADDR_1,
                 Pin.board.ADC_ADDR_2,
                 Pin.board.ADC_ADDR_3)
adc_mux_addrs[0].init(Pin.OUT, value=False)
adc_mux_addrs[1].init(Pin.OUT, value=False)
adc_mux_addrs[2].init(Pin.OUT, value=False)

adc_io_chip = tca.get_chip(Pin.board.ADC_ADDR_1)
adc_io_ens_addrs = (1 << tca.get_number(Pin.board.ADC_MUX_EN_1),
                    1 << tca.get_number(Pin.board.ADC_MUX_EN_2))
adc_io_adc_addrs = (1 << tca.get_number(Pin.board.ADC_ADDR_1),
                    1 << tca.get_number(Pin.board.ADC_ADDR_2),
                    1 << tca.get_number(Pin.board.ADC_ADDR_3))
adc_io_mask = adc_io_ens_addrs[0] | adc_io_ens_addrs[1] | \
              adc_io_adc_addrs[0] | adc_io_adc_addrs[1] | adc_io_adc_addrs[2]


# Shared analog input
shared_adc = ADC(Pin.board.SHARED_ADC)


def enable_main_output():
    main_en.value(True)
    time.sleep(1)  # Time for capacitor to charge
    print("> Output enabled")

def disable_main_output():
    main_en.value(False)
    print("> Output disabled")

def deselect_address():
    adc_mux_ens[0].value(False)
    adc_mux_ens[1].value(False)

def select_address(address):
    if address < 0:
        raise ValueError("address is less than zero")
    elif address > 0b1111:
        raise ValueError("address is greater than number of available addresses")
    else:
        state = 0x0000

        if address & 0b0001 > 0:
            state |= adc_io_adc_addrs[0]

        if address & 0b0010 > 0:
            state |= adc_io_adc_addrs[1]

        if address & 0b0100 > 0:
            state |= adc_io_adc_addrs[2]

        if address & 0b1000 > 0:
            state |= adc_io_ens_addrs[0]
        else:
            state |= adc_io_ens_addrs[1]

        tca.change_output_mask(adc_io_chip, adc_io_mask, state)

def sample_shared_adc(address, samples):
    select_address(address)
    time.sleep(0.1)
    adc_int = 0
    for i in range(samples):
        adc_int += shared_adc.read_u16()
        # time.sleep(0.0001)
    adc_int = int(round(adc_int / samples, 0))
    return adc_int, raw_to_flt(adc_int)

def raw_to_flt(raw):
    return (raw * 3.3) / 65536 # TODO check if 65536 or 65535

def raws_avg(raws):
    raw_avg = 0
    if isinstance(raws, (int, float)):
        return raws

    for raw in raws:
        raw_avg += raw
    raw_avg /= len(raws)
    return int(round(raw_avg, 0))

def map_float(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Yukon Unit:            0    1    2    3    4    5    6    7    8    9
VI_ZERO_MEASURED_RAWS = (534, 456, 503, 395, 320, 340, 315, 382, 533, 450)
VI_ZERO_MEASURED_AVG = raws_avg(VI_ZERO_MEASURED_RAWS)
VI_ZERO_MEASURED = raw_to_flt(VI_ZERO_MEASURED_AVG)

# Yukon Unit:            0    1    2    3    4    5    6    7    8    9
VO_ZERO_MEASURED_RAWS = (695, 608, 667, 552, 475, 491, 470, 539, 692, 605)
VO_ZERO_MEASURED_AVG = raws_avg(VO_ZERO_MEASURED_RAWS)
VO_ZERO_MEASURED = raw_to_flt(VO_ZERO_MEASURED_AVG)

# Yukon Unit:            0      1      2      3      4      5      6      7      8      9
VI_FIVE_MEASURED_RAWS = (13666, 13700, 13787, 13645, 13573, 13693, 13535, 13639, 13728, 13802)
VI_FIVE_MEASURED_AVG = raws_avg(VI_FIVE_MEASURED_RAWS)
VI_FIVE_MEASURED = raw_to_flt(VI_FIVE_MEASURED_AVG)

# Yukon Unit:            0      1      2      3      4      5      6      7      8      9
VO_FIVE_MEASURED_RAWS = (13920, 13758, 13830, 13779, 13687, 13670, 13646, 13765, 13762, 13780)
VO_FIVE_MEASURED_AVG = raws_avg(VO_FIVE_MEASURED_RAWS)
VO_FIVE_MEASURED = raw_to_flt(VO_FIVE_MEASURED_AVG)

# Yukon Unit:                 0      1      2      3      4      5      6      7      8      9
VI_SEVENTEEN_MEASURED_RAWS = (46159, 45798, 45906, 45767, 45688, 46068, 45580, 45784, 45776, 46215)
VI_SEVENTEEN_MEASURED_AVG = raws_avg(VI_SEVENTEEN_MEASURED_RAWS)
VI_SEVENTEEN_MEASURED = raw_to_flt(VI_SEVENTEEN_MEASURED_AVG)

# Yukon Unit:                 0      1      2      3      4      5      6      7      8      9
VO_SEVENTEEN_MEASURED_RAWS = (45888, 45575, 45627, 45809, 45651, 45577, 45469, 45802, 45346, 45615)
VO_SEVENTEEN_MEASURED_AVG = raws_avg(VO_SEVENTEEN_MEASURED_RAWS)
VO_SEVENTEEN_MEASURED = raw_to_flt(VO_SEVENTEEN_MEASURED_AVG)


# Yukon Unit:                  0    1    2    3    4    5    6    7    8    9
C_MILLITHIRTY_MEASURED_RAWS = (522, 439, 472, 350, 317, 315, 287, 356, 491, 422)
C_MILLITHIRTY_MEASURED_AVG = raws_avg(C_MILLITHIRTY_MEASURED_RAWS)
C_MILLITHIRTY_MEASURED = raw_to_flt(C_MILLITHIRTY_MEASURED_AVG)

# Yukon Unit:          0     1     2     3     4    5    6    7    8     9
C_ONE_MEASURED_RAWS = (1172, 1054, 1040, 1030, 928, 948, 916, 899, 1066, 1094)
C_ONE_MEASURED_AVG = raws_avg(C_ONE_MEASURED_RAWS)
C_ONE_MEASURED = raw_to_flt(C_ONE_MEASURED_AVG)

# Yukon Unit:          0     1     2     3     4     5     6     7     8     9
C_TWO_MEASURED_RAWS = (2139, 2045, 2108, 2014, 1883, 1925, 1932, 1948, 2124, 2099)
C_TWO_MEASURED_AVG = raws_avg(C_TWO_MEASURED_RAWS)
C_TWO_MEASURED = raw_to_flt(C_TWO_MEASURED_AVG)

# Yukon Unit:            0     1     2     3     4     5     6     7     8     9
C_THREE_MEASURED_RAWS = (3096, 3003, 3092, 2973, 2826, 2873, 2895, 2936, 3090, 3054)
C_THREE_MEASURED_AVG = raws_avg(C_THREE_MEASURED_RAWS)
C_THREE_MEASURED = raw_to_flt(C_THREE_MEASURED_AVG)

# Yukon Unit:           0     1     2     3     4     5     6     7     8     9
C_FOUR_MEASURED_RAWS = (4060, 3954, 4053, 3920, 3764, 3819, 3849, 3892, 4040, 4010)
C_FOUR_MEASURED_AVG = raws_avg(C_FOUR_MEASURED_RAWS)
C_FOUR_MEASURED = raw_to_flt(C_FOUR_MEASURED_AVG)

# Yukon Unit:           0     1     2     3     4     5     6     7     8     9
C_FIVE_MEASURED_RAWS = (5026, 4885, 5010, 4849, 4688, 4750, 4803, 4824, 4984, 4960)
C_FIVE_MEASURED_AVG = raws_avg(C_FIVE_MEASURED_RAWS)
C_FIVE_MEASURED = raw_to_flt(C_FIVE_MEASURED_AVG)

# Yukon Unit:          0     1     2     3     4     5     6     7     8     9
C_SIX_MEASURED_RAWS = (5988, 5838, 5966, 5797, 5629, 5696, 5758, 5774, 5937, 5921)
C_SIX_MEASURED_AVG = raws_avg(C_SIX_MEASURED_RAWS)
C_SIX_MEASURED = raw_to_flt(C_SIX_MEASURED_AVG)

# Yukon Unit:            0     1     2     3     4     5     6     7     8     9
C_SEVEN_MEASURED_RAWS = (6962, 6803, 6927, 6753, 6577, 6650, 6715, 6731, 6898, 6890)
C_SEVEN_MEASURED_AVG = raws_avg(C_SEVEN_MEASURED_RAWS)
C_SEVEN_MEASURED = raw_to_flt(C_SEVEN_MEASURED_AVG)

# Yukon Unit:            0     1     2     3     4     5     6     7     8     9
C_EIGHT_MEASURED_RAWS = (7926, 7755, 7884, 7700, 7518, 7599, 7670, 7682, 7854, 7852)
C_EIGHT_MEASURED_AVG = raws_avg(C_EIGHT_MEASURED_RAWS)
C_EIGHT_MEASURED = raw_to_flt(C_EIGHT_MEASURED_AVG)

# Yukon Unit:           0     1     2     3     4     5     6     7     8     9
C_NINE_MEASURED_RAWS = (8730, 8533, 8685, 8467, 8292, 8383, 8465, 8460, 8640, 8641)
C_NINE_MEASURED_AVG = raws_avg(C_NINE_MEASURED_RAWS)
C_NINE_MEASURED = raw_to_flt(C_NINE_MEASURED_AVG)

# Yukon Unit:          0     1     2     3     4     5     6     7     8     9
C_TEN_MEASURED_RAWS = (9696, 9489, 9641, 9416, 9234, 9332, 9420, 9412, 9596, 9603)
C_TEN_MEASURED_AVG = raws_avg(C_TEN_MEASURED_RAWS)
C_TEN_MEASURED = raw_to_flt(C_TEN_MEASURED_AVG)

# Yukon Unit:              0      1      2      3      4      5      6      7      8      9
C_FIFTEEN_MEASURED_RAWS = (14544, 14257, 14445, 14155, 13937, 14067, 14205, 14153, 14372, 14414)
C_FIFTEEN_MEASURED_AVG = raws_avg(C_FIFTEEN_MEASURED_RAWS)
C_FIFTEEN_MEASURED = raw_to_flt(C_FIFTEEN_MEASURED_AVG)

print("STARTED")
print("ViZero =", VI_ZERO_MEASURED_AVG)
print("ViFive =", VI_FIVE_MEASURED_AVG)
print("ViSeventeen =", VI_SEVENTEEN_MEASURED_AVG)
print()
print("VoZero =", VO_ZERO_MEASURED_AVG)
print("VoFive =", VO_FIVE_MEASURED_AVG)
print("VoSeventeen =", VO_SEVENTEEN_MEASURED_AVG)
print()
print("CMilliThirty =", C_MILLITHIRTY_MEASURED_AVG)
print("COne =", C_ONE_MEASURED_AVG)
print("CTwo =", C_TWO_MEASURED_AVG)
print("CThree =", C_THREE_MEASURED_AVG)
print("CFour =", C_FOUR_MEASURED_AVG)
print("CFive =", C_FIVE_MEASURED_AVG)
print("CSix =", C_SIX_MEASURED_AVG)
print("CSeven =", C_SEVEN_MEASURED_AVG)
print("CEight =", C_EIGHT_MEASURED_AVG)
print("CNine =", C_NINE_MEASURED_AVG)
print("CTen =", C_TEN_MEASURED_AVG)
print("CFifteen =", C_FIFTEEN_MEASURED_AVG)

enable_main_output()

while True:
    # Read the input voltage sense
    vi_raw, vi_flt = sample_shared_adc(VOLTAGE_IN_SENSE_ADDR, 1000000)
    if vi_raw >= VI_FIVE_MEASURED_AVG:
        vi_mapped = map_float(vi_flt, VI_FIVE_MEASURED, VI_SEVENTEEN_MEASURED, 5, 17)
    else:
        vi_mapped = map_float(vi_flt, VI_ZERO_MEASURED, VI_FIVE_MEASURED, 0, 5)
    print("ViRaw = ", vi_raw, ", ViFlt = ", vi_flt, ", ViMapped = ", vi_mapped, sep="", end=", ")
    
    # Read the output voltage sense
    select_address(VOLTAGE_OUT_SENSE_ADDR)
    vo_raw, vo_flt = sample_shared_adc(VOLTAGE_OUT_SENSE_ADDR, 1000000)
    if vo_raw >= VO_FIVE_MEASURED_AVG:
        vo_mapped = map_float(vo_flt, VO_FIVE_MEASURED, VO_SEVENTEEN_MEASURED, 5, 17)
    else:
        vo_mapped = map_float(vo_flt, VO_ZERO_MEASURED, VO_FIVE_MEASURED, 0, 5)
    print("VoRaw = ", vo_raw, ", VoFlt = ", vo_flt, ", VoMapped = ", vo_mapped, sep="", end=", ")

    # Read the current sense
    c_raw, c_flt = sample_shared_adc(CURRENT_SENSE_ADDR, 1000000)
    c_mapped = map_float(c_flt, C_ONE_MEASURED, C_FIFTEEN_MEASURED, 1, 15)
    print("CRaw = ", c_raw, ", CFlt = ", c_flt, ", CMapped = ", c_mapped, sep="")
