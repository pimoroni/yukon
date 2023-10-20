### Quad Servo Direct Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Quad Servo Direct Module for Yukon](https://pimoroni.com/yukon).

- [Constants](#constants)
- [Variables \& Properties](#variables--properties)
- [Methods](#methods)



#### Constants
```python
NAME = "Quad Servo Direct"
NUM_SERVOS = 4
```

#### Variables & Properties
```python
servos : list[Servo]
servo1 -> Servo
servo2 -> Servo
servo3 -> Servo
servo4 -> Servo
```

#### Methods
```python
## Address Checking ##
@staticmethod
is_module(adc1_level : int, adc2_level : int, slow1 : bool, slow2 : bool, slow3 :bool) -> bool

## Initialisation ##
QuadServoDirect()
initialise(slot : SLOT, adc1_func : Any, adc2_func : Any) -> None
reset() -> None

## Sensing ##
read_adc1() -> float
read_adc2() -> float
```

