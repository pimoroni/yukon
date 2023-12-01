# Yukon Module - Library Reference <!-- omit in toc -->

This is the library reference for the parent class of all Yukon modules.

- [Reference](#reference)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Methods](#methods)


## Reference

### Constants

```python
NAME = "Unknown"
```

### Variables

```python
slot: SLOT
```

### Methods

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3: bool) -> bool  # Override in child Module class

# Initialisation
YukonModule()
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None    # Override in child Module class
is_initialised() -> bool
deregister() -> None
reset() -> None                 # Override in child Module class

# Monitoring
assign_monitor_action(callback_function: Callable)
monitor() -> None               # Override in child Module class
get_readings() -> OrderedDict   # Override in child Module class
get_formatted_readings(allowed: string | tuple[string] | list[string]=None,
                       excluded: string | tuple[string] | list[string]=None)
print_readings(allowed: string | tuple[string] | list[string]=None,
               excluded: string | tuple[string] | list[string]=None)
process_readings() -> None      # Override in child Module class
clear_readings() -> None        # Override in child Module class
```
