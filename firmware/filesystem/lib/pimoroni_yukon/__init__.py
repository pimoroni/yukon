# The entire lib dir gets added to a LittleFS filesystem and appended to the firmware
from machine import Pin
from ucollections import namedtuple

Slot = namedtuple("Slot", ("ID",
                           "FAST1",
                           "FAST2",
                           "FAST3",
                           "FAST4",
                           "SLOW1",
                           "SLOW2",
                           "SLOW3",
                           "ADC1_ADDR",
                           "ADC2_TEMP_ADDR"))

SLOT1 = Slot(1,
             Pin.board.SLOT1_FAST1,
             Pin.board.SLOT1_FAST2,
             Pin.board.SLOT1_FAST3,
             Pin.board.SLOT1_FAST4,
             Pin.board.SLOT1_SLOW1,
             Pin.board.SLOT1_SLOW2,
             Pin.board.SLOT1_SLOW3,
             0,  # 0b0000
             3   # 0b0011
             ) 

SLOT2 = Slot(2,
             Pin.board.SLOT2_FAST1,
             Pin.board.SLOT2_FAST2,
             Pin.board.SLOT2_FAST3,
             Pin.board.SLOT2_FAST4,
             Pin.board.SLOT2_SLOW1,
             Pin.board.SLOT2_SLOW2,
             Pin.board.SLOT2_SLOW3,
             1,  # 0b0001
             6   # 0b0110
             )

SLOT3 = Slot(3,
             Pin.board.SLOT3_FAST1,
             Pin.board.SLOT3_FAST2,
             Pin.board.SLOT3_FAST3,
             Pin.board.SLOT3_FAST4,
             Pin.board.SLOT3_SLOW1,
             Pin.board.SLOT3_SLOW2,
             Pin.board.SLOT3_SLOW3,
             4,  # 0b0100
             2   # 0b0010
             )

SLOT4 = Slot(4,
             Pin.board.SLOT4_FAST1,
             Pin.board.SLOT4_FAST2,
             Pin.board.SLOT4_FAST3,
             Pin.board.SLOT4_FAST4,
             Pin.board.SLOT4_SLOW1,
             Pin.board.SLOT4_SLOW2,
             Pin.board.SLOT4_SLOW3,
             5,  # 0b0101
             7   # 0b0111
             )

SLOT5 = Slot(5,
             Pin.board.SLOT5_FAST1,
             Pin.board.SLOT5_FAST2,
             Pin.board.SLOT5_FAST3,
             Pin.board.SLOT5_FAST4,
             Pin.board.SLOT5_SLOW1,
             Pin.board.SLOT5_SLOW2,
             Pin.board.SLOT5_SLOW3,
             8,  # 0b1000
             11  # 0b1011
             )

SLOT6 = Slot(6,
             Pin.board.SLOT6_FAST1,
             Pin.board.SLOT6_FAST2,
             Pin.board.SLOT6_FAST3,
             Pin.board.SLOT6_FAST4,
             Pin.board.SLOT6_SLOW1,
             Pin.board.SLOT6_SLOW2,
             Pin.board.SLOT6_SLOW3,
             9,  # 0b1001
             10  # 0b1010
             )
