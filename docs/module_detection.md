# Pimoroni Yukon - Module Detection <!-- omit in toc -->

- [How it Works](#how-it-works)
  - [IO States](#io-states)
  - [Multiple Addresses](#multiple-addresses)
- [Address Table](#address-table)

## How it Works

Yukon detects which modules are attached to it by reading the state of each slot's ADC and SLOW IO pin prior to module initialisation and power-up. This forms an "address" that is used to verify that the module attached to a slot matches what the code has been configured with, preventing unexpected or potentially dangerous behaviour.

### IO States

Below are the states that the two ADC pins and three SLOW IO pins support.
| Pin   | States               | Disconnected State                    |
|-------|----------------------|---------------------------------------|
| ADC1  | LOW or FLOAT or HIGH | FLOAT                                 |
| ADC2  | LOW or FLOAT or HIGH | HIGH (due to thermistor 5.1k pull-up) |
| SLOW1 | LOW or HIGH          | HIGH (due to IO expander pull-up)     |
| SLOW2 | LOW or HIGH          | HIGH (due to IO expander pull-up)     |
| SLOW3 | LOW or HIGH          | HIGH (due to IO expander pull-up)     |

Also shown is the state these pins will have if they are left disconnected, such as when a slot is empty. **This "address" should be avoided by any custom module**.

### Multiple Addresses

If a module does not have a single state it can start in, or it retains a state from a previous power-up, then it will need to be assigned multiple addresses. All modules that feature an onboard thermistor automatically take up three addresses minimum to account for the different temperatures the sensor can read during detection. Similarly, any modules that expose an ADC pin to the user will automatically require addresses to cover the full voltage range of that pin, with the worst case being 9 addresses if both ADC1 and ADC2 are user accessible.


## Address Table

Here is the current address list for Yukon modules produced by Pimoroni.

<table>
    <thead>
        <tr>
            <th>ADC1</th><th>ADC2</th><th>SLOW1</th><th>SLOW2</th><th>SLOW3</th><th>Module</th><th>Condition (if any)</th>
        </tr>
    </thead>
    <tbody>
        <!-- Quad Servo Direct -->
        <tr style="background-color:rgba(182, 215, 168, 0.25);">
            <td rowspan=3>LOW</td>
            <td>LOW</td>
            <td rowspan=9>0</td>
            <td rowspan=9>0</td>
            <td rowspan=9>0</td>
            <td rowspan=9>Quad Servo Direct</td>
            <td>A1 low, A2 low</td>
        </tr>
        <tr style="background-color:rgba(182, 215, 168, 0.25);">
            <td>FLOAT</td>
            <td>A1 low, A2 mid</td>
        </tr>
        <tr style="background-color:rgba(182, 215, 168, 0.25);">
            <td>HIGH</td>
            <td>A1 low, A2 high</td>
        </tr>
        <tr style="background-color:rgba(182, 215, 168, 0.25);">
            <td rowspan=3>FLOAT</td>
            <td>LOW</td>
            <td>A1 mid, A2 low</td>
        </tr>
        <tr style="background-color:rgba(182, 215, 168, 0.25);">
            <td>FLOAT</td>
            <td>A1 mid, A2 mid</td>
        </tr>
        <tr style="background-color:rgba(182, 215, 168, 0.25);">
            <td>HIGH</td>
            <td>A1 mid, A2 high</td>
        </tr>
        <tr style="background-color:rgba(182, 215, 168, 0.25);">
            <td rowspan=3>HIGH</td>
            <td>LOW</td>
            <td>A1 high, A2 low</td>
        </tr>
        <tr style="background-color:rgba(182, 215, 168, 0.25);">
            <td>FLOAT</td>
            <td>A1 high, A2 mid</td>
        </tr>
        <tr style="background-color:rgba(182, 215, 168, 0.25);">
            <td>HIGH</td>
            <td>A1 high, A2 high</td>
        </tr>
        <!-- Big Motor -->
        <tr style="border-top: 2px solid; background-color:rgba(180, 167, 214, 0.25);">
            <td rowspan=3>LOW</td>
            <td>LOW</td>
            <td rowspan=3>0</td>
            <td rowspan=3>0</td>
            <td rowspan=3>1</td>
            <td rowspan=3>Big Motor + Encoder</td>
            <td rowspan=3>No Fault</td>
        </tr>
        <tr style="background-color:rgba(180, 167, 214, 0.25);">
            <td>FLOAT</td>
        </tr>
        <tr style="background-color:rgba(180, 167, 214, 0.25);">
            <td>HIGH</td>
        </tr>
        <!-- Vacant -->
        <tr style="border-top: 1.5px dotted;">
            <td>FLOAT</td><td>LOW</td><td>0</td><td>0</td><td>1</td><td></td><td></td>
        </tr>
        <tr>
            <td>FLOAT</td><td>FLOAT</td><td>0</td><td>0</td><td>1</td><td></td><td></td>
        </tr>
        <tr>
            <td>FLOAT</td><td>HIGH</td><td>0</td><td>0</td><td>1</td><td></td><td></td>
        </tr>
        <!-- Dual Motor / Bipolar Stepper -->
        <tr style="border-top: 1.5px dotted; background-color:rgba(249, 203, 156, 0.25);">
            <td rowspan=3>HIGH</td>
            <td>LOW</td>
            <td rowspan=3>0</td>
            <td rowspan=3>0</td>
            <td rowspan=3>1</td>
            <td rowspan=3>Dual Motor</td>
            <td rowspan=3></td>
        </tr>
        <tr style="background-color:rgba(249, 203, 156, 0.25);">
            <td>FLOAT</td>
        </tr>
        <tr style="background-color:rgba(249, 203, 156, 0.25);">
            <td>HIGH</td>
        </tr>
        <!-- Vacant -->
        <tr style="border-top: 2px solid;">
            <td>LOW</td><td>LOW</td><td>0</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <tr>
            <td>LOW</td><td>FLOAT</td><td>0</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <tr>
            <td>LOW</td><td>HIGH</td><td>0</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <!-- Vacant -->
        <tr style="border-top: 1.5px dotted;">
            <td>FLOAT</td><td>LOW</td><td>0</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <tr>
            <td>FLOAT</td><td>FLOAT</td><td>0</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <tr>
            <td>FLOAT</td><td>HIGH</td><td>0</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <!-- Quad Servo Regulated -->
        <tr style="border-top: 1.5px dotted; background-color:rgba(159, 197, 232, 0.25);">
            <td rowspan=3>HIGH</td>
            <td>LOW</td>
            <td rowspan=3>0</td>
            <td rowspan=3>1</td>
            <td rowspan=3>0</td>
            <td rowspan=3>Quad Servo Regulated</td>
            <td rowspan=3>Power Not Good</td>
        </tr>
        <tr style="background-color:rgba(159, 197, 232, 0.25);">
            <td>FLOAT</td>
        </tr>
        <tr style="background-color:rgba(159, 197, 232, 0.25);">
            <td>HIGH</td>
        </tr>
        <!-- Big Motor + Encoder -->
        <tr style="border-top: 2px solid; background-color:rgba(180, 167, 214, 0.25);">
            <td rowspan=3>LOW</td>
            <td>LOW</td>
            <td rowspan=3>0</td>
            <td rowspan=3>1</td>
            <td rowspan=3>1</td>
            <td rowspan=3>Big Motor + Encoder</td>
            <td rowspan=3>Faulted</td>
        </tr>
        <tr style="background-color:rgba(180, 167, 214, 0.25);">
            <td>FLOAT</td>
        </tr>
        <tr style="background-color:rgba(180, 167, 214, 0.25);">
            <td>HIGH</td>
        </tr>
        <!-- Audio Amp -->
        <tr style="border-top: 1.5px dotted; background-color:rgba(109, 158, 235, 0.25);">
            <td rowspan=3>FLOAT</td>
            <td>LOW</td>
            <td rowspan=3>0</td>
            <td rowspan=3>1</td>
            <td rowspan=3>1</td>
            <td rowspan=3>Audio Amp Mono</td>
            <td rowspan=3></td>
        </tr>
        <tr style="background-color:rgba(109, 158, 235, 0.25);">
            <td>FLOAT</td>
        </tr>
        <tr style="background-color:rgba(109, 158, 235, 0.25);">
            <td>HIGH</td>
        </tr>
        <!-- Quad Servo Regulated -->
        <tr style="border-top: 1.5px dotted; background-color:rgba(159, 197, 232, 0.25);">
            <td rowspan=3>HIGH</td>
            <td>LOW</td>
            <td rowspan=3>0</td>
            <td rowspan=3>1</td>
            <td rowspan=3>1</td>
            <td rowspan=3>Quad Servo Regulated</td>
            <td rowspan=3>Power Good</td>
        </tr>
        <tr style="background-color:rgba(159, 197, 232, 0.25);">
            <td>FLOAT</td>
        </tr>
        <tr style="background-color:rgba(159, 197, 232, 0.25);">
            <td>HIGH</td>
        </tr>
        <!-- Bench Power -->
        <tr style="border-top: 2px solid; background-color:rgba(221, 126, 107, 0.25);">
            <td rowspan=3>LOW</td>
            <td>LOW</td>
            <td rowspan=6>1</td>
            <td rowspan=6>0</td>
            <td rowspan=6>0</td>
            <td rowspan=6>Bench Power</td>
            <td rowspan=3>Output Discharged</td>
        </tr>
        <tr style="background-color:rgba(221, 126, 107, 0.25);">
            <td>FLOAT</td>
        </tr>
        <tr style="background-color:rgba(221, 126, 107, 0.25);">
            <td>HIGH</td>
        </tr>
        <tr style="background-color:rgba(221, 126, 107, 0.25);">
            <td rowspan=3>FLOAT</td>
            <td>LOW</td>
            <td rowspan=3>Output Discharging</td>
        </tr>
        <tr style="background-color:rgba(221, 126, 107, 0.25);">
            <td>FLOAT</td>
        </tr>
        <tr style="background-color:rgba(221, 126, 107, 0.25);">
            <td>HIGH</td>
        </tr>
        <!-- Vacant -->
        <tr style="border-top: 1.5px dotted;">
            <td>HIGH</td><td>LOW</td><td>1</td><td>0</td><td>0</td><td></td><td></td>
        </tr>
        <!-- Reserved -->
        <tr style="background-color:rgba(128, 128, 128, 0.25);">
            <td>HIGH</td><td>FLOAT</td><td>1</td><td>0</td><td>0</td><td>Reserved</td><td></td>
        </tr>
        <!-- Serial Bus Servo -->
        <tr style="background-color:rgba(244, 204, 204, 0.25);">
            <td>HIGH</td><td>HIGH</td><td>1</td><td>0</td><td>0</td><td>Serial Bus Servo</td><td></td>
        </tr>
        <!-- Reserved -->
        <tr style="border-top: 2px solid; background-color:rgba(128, 128, 128, 0.25);">
            <td>LOW</td><td>LOW</td><td>1</td><td>0</td><td>1</td><td>Reserved</td><td></td>
        </tr>
        <tr style="background-color:rgba(128, 128, 128, 0.25);">
            <td>LOW</td><td>FLOAT</td><td>1</td><td>0</td><td>1</td><td>Reserved</td><td></td>
        </tr>
        <tr style="background-color:rgba(128, 128, 128, 0.25);">
            <td>LOW</td><td>HIGH</td><td>1</td><td>0</td><td>1</td><td>Reserved</td><td></td>
        </tr>
        <!-- Dual Switched Output -->
        <tr style="border-top: 1.5px dotted; background-color:rgba(213, 166, 189, 0.25);">
            <td rowspan=3>FLOAT</td>
            <td>LOW</td>
            <td rowspan=3>1</td>
            <td rowspan=3>0</td>
            <td rowspan=3>1</td>
            <td rowspan=3>Dual Switched Output</td>
            <td rowspan=3></td>
        </tr>
        <tr style="background-color:rgba(213, 166, 189, 0.25);">
            <td>FLOAT</td>
        </tr>
        <tr style="background-color:rgba(213, 166, 189, 0.25);">
            <td>HIGH</td>
        </tr>
        <!-- Vacant -->
        <tr style="border-top: 1.5px dotted;">
            <td>HIGH</td><td>LOW</td><td>1</td><td>0</td><td>1</td><td></td><td></td>
        </tr>
        <tr>
            <td>HIGH</td><td>FLOAT</td><td>1</td><td>0</td><td>1</td><td></td><td></td>
        </tr>
        <tr>
            <td>HIGH</td><td>HIGH</td><td>1</td><td>0</td><td>1</td><td></td><td></td>
        </tr>
        <tr style="border-top: 2px solid;">
            <td>LOW</td><td>LOW</td><td>1</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <tr>
            <td>LOW</td><td>FLOAT</td><td>1</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <!-- Proto Potentiometer -->
        <tr style="background-color:rgba(162, 196, 201, 0.25);">
            <td>LOW</td><td>HIGH</td><td>1</td><td>1</td><td>0</td><td>Proto Potentiometer</td><td>Min Position</td>
        </tr>
        <!-- Vacant -->
        <tr style="border-top: 1.5px dotted;">
            <td>FLOAT</td><td>LOW</td><td>1</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <tr>
            <td>FLOAT</td><td>FLOAT</td><td>1</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <!-- Proto Potentiometer -->
        <tr style="background-color:rgba(162, 196, 201, 0.25);">
            <td>FLOAT</td><td>HIGH</td><td>1</td><td>1</td><td>0</td><td>Proto Potentiometer</td><td>Between Min and Max</td>
        </tr>
        <!-- Vacant -->
        <tr style="border-top: 1.5px dotted;">
            <td>HIGH</td><td>LOW</td><td>1</td><td>1</td><td>0</td><td></td><td></td>
        </tr>
        <!-- Reserved -->
        <tr style="background-color:rgba(128, 128, 128, 0.25);">>
            <td>HIGH</td><td>FLOAT</td><td>1</td><td>1</td><td>0</td><td>Reserved</td><td></td>
        </tr>
        <!-- Proto Potentiometer -->
        <tr style="background-color:rgba(162, 196, 201, 0.25);">
            <td>HIGH</td><td>HIGH</td><td>1</td><td>1</td><td>0</td><td>Proto Potentiometer</td><td>Max Position</td>
        </tr>
        <!-- LED Strip -->
        <tr style="border-top: 2px solid; background-color:rgba(255, 229, 153, 0.25);">
            <td rowspan=3>LOW</td>
            <td>LOW</td>
            <td rowspan=3>1</td>
            <td rowspan=3>1</td>
            <td rowspan=3>1</td>
            <td rowspan=3>LED Strip</td>
            <td rowspan=3></td>
        </tr>
        <tr style="background-color:rgba(255, 229, 153, 0.25);">
            <td>FLOAT</td>
        </tr>
        <tr style="background-color:rgba(255, 229, 153, 0.25);">
            <td>HIGH</td>
        </tr>
        <!-- Vacant -->
        <tr style="border-top: 1.5px dotted;">
            <td>FLOAT</td><td>LOW</td><td>1</td><td>1</td><td>1</td><td></td><td></td>
        </tr>
        <tr>
            <td>FLOAT</td><td>FLOAT</td><td>1</td><td>1</td><td>1</td><td></td><td></td>
        </tr>
        <!-- Empty Slot -->
        <tr style="background-color:rgba(128, 128, 128, 0.25);">
            <td>FLOAT</td><td>HIGH</td><td>1</td><td>1</td><td>1</td><td>Empty Slot</td><td></td>
        </tr>
        <!-- Reserved -->
        <tr style="border-top: 1.5px dotted; background-color:rgba(128, 128, 128, 0.25);">
            <td>HIGH</td><td>LOW</td><td>1</td><td>1</td><td>1</td><td>Reserved</td><td></td>
        </tr>
        <tr style="background-color:rgba(128, 128, 128, 0.25);">
            <td>HIGH</td><td>FLOAT</td><td>1</td><td>1</td><td>1</td><td>Reserved</td><td></td>
        </tr>
        <tr style="border-bottom: 2px solid;background-color:rgba(128, 128, 128, 0.25);">
            <td>HIGH</td><td>HIGH</td><td>1</td><td>1</td><td>1</td><td>Reserved</td><td></td>
        </tr>
    </tbody>
</table>
