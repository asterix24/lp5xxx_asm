#!/bin/env python

def op_nop(labels, inst):
    print("NOP", end="->")
    return []

def op_dw(labels, inst):
    MAX=0b0000000111111111
    MIN=0

    try:
        value = inst['args'][0]
    except IndexError as e:
        raise ValueError(f"Missing data [{inst['args']}]")

    try:
        if "b" in value:
            value = int(value.replace("b",""),2)
        elif "0x" in value:
            value = int(value,16)
        else:
            value = int(value)
    except ValueError as e:
        raise ValueError(f"Wrong data type [{inst['args']}]")

    if value > MAX or value < MIN:
        raise ValueError(f"Data outside limits [{inst['args']}]")

    vh = f"0x{((value & 0xff00) >> 8):02x}"
    vl = f"0x{(value & 0x00ff):02x}"

    return [vh, vl]

def op_map_addr(labels, inst):
    """
    The map_addr instruction sets the index pointer to point to the mapping table row
    defined by bits [6:0] and sets the row active. The engine does not push a new PWM
    value to the LED driver output before the set_pwm or ramp instruction is executed.
    If the mapping has been released from an LED, the value in the PWM register still
    controls the LED brightness.

    |NAME         |VALUE (d) |  DESCRIPTION
    |SRAM address | 0–127    | SRAM address containing mapping data restricted to lower half of memory.

    """
    OP=0b1001111110000000
    MAX=127
    try:
        args = inst['args'][0]
    except IndexError as e:
        raise ValueError(f"Missing data [{inst['args']}]")

    if args not in labels:
        raise ValueError(f"No valid label [{inst['args']}]")

    addr = int(labels[args])
    print(addr)
    if addr > 127:
        raise ValueError(f"Invalid addrs[{inst['args']}]")

    value = OP | addr
    vh = f"0x{((value & 0xff00) >> 8):02x}"
    vl = f"0x{(value & 0x00ff):02x}"

    return [vh, vl]

def op_ramp(labels, inst):
    """
    This is the instruction useful for smoothly changing from one PWM value
    into another PWM value on the LED0 to LED8 outputs —in other words,
    generating ramps with a negative or positive slope. The LP5569 device
    allows the programming of very fast and very slow ramps using only a single
    instruction. Full ramp 0 to 255 ramp time ranges from 124 ms to 4 s. The
    ramp instruction generates a PWM ramp, using the effective PWM value as a
    starting value. At each ramp step the output is incremented or decremented
    by 1, unless the number of increments is 0. The time span for one ramp step
    is defined with the prescale bit [14] and step-time bits [13:9]. The ramp
    instruction controls the eight most-significant bits (MSB) of the PWM
    values and the remaining bits are interpolated as ramp mid-values
    internally for smoother transition. Prescale = 0 sets a 0.49-ms cycle time
    and prescale = 1 sets a 15.6-ms cycle time; so the minimum time span for
    one step is 0.49 ms (prescale × step time span = 0.49 ms × 1) and the
    maximum time span is 15.6 ms × 31 = 484 ms/step. If all the step-time bits
    [13:9] are set to zero, the output value is incremented or decremented
    during one prescale on the whole time cycle. The number-of-increments value
    defines how many steps are taken during one ramp instruction: the increment
    maximum value is 255, which corresponds to an increment from zero value to
    the maximum value. If PWM reaches the minimum or maximum value (0 or 255)
    during the ramp instruction, the ramp instruction is executed to the end
    regardless of saturation. This enables ramp instruction to be used as a
    combined ramp-and-wait instruction. Note: the ramp instruction is a wait
    instruction when the increment bits [7:0] are set to zero.

    Programming ramps with variables is very similar to programming ramps with
    numerical operands. The only difference is that step time and number of
    increments are captured from variable registers when the instruction
    execution is started. If the variables are updated after starting the
    instruction execution, it has no effect on instruction execution. Again, at
    each ramp step the output is incremented or decremented by 1 unless the
    step time is 0 or the number of increments is 0. The time span for one step
    is defined with the prescale and step-time bits. The step time is defined
    with variable A, B, C, or D. Variable A is set by an I2C write to the
    engine 1, 2, or 3 variable A register or the ld instruction, variables B
    and C are set with the ld instruction, and variable D is set by an I2C
    write to the variable D register. Setting the EXP_EN bit of registers
    07h–0Fh high or low sets the exponential (1) or linear ramp (0). By using
    the exponential ramp setting, the visual effect appears like a linear ramp
    to the human eye.

    NAME              | VARIABLE | VALUE (d)| DESCRIPTION
    prescale          | Numeric  | 0        | 32.7 kHz / 16 ≥ 0.488 ms cycle time
                    |          | 1        | 32.7 kHz / 512 ≥ 15.625 ms cycle time
    sign              | Numeric  | 0        | Increase PWM output
                    |          | 1        | Decrease PWM output
    step time         | Numeric  | 1-31     | One ramp increment done is in step time × prescale.
                    | Variable | 0-3      |  Value in the variable A, B, C, or D must be from 
    no. of increments | Numeric  | 0-255    |  1 to 31 for correct operation.
                    | Variable | 0-3      | The number of ramp cycles. Variables A to D as input.
    """
    OP_PARAM=0b0000000000000000
    OP_VAR  =0b1000010000000000
    prescale = 0
    sign = 0
    step_time = 0
    no_increment = 0

    try:
        ramp_time = float(inst['args'][0])
        level = int(inst['args'][1])
    except IndexError as e:
        raise ValueError(f"Missing data [{inst['args']}]")

    variable = False
    try:
        ramp_time = int(ramp_time) * 1000 # for convenienze is bettere in ms
    except ValueError as e:
        variable = True

    if not variable:
        if level < 0:
            sign = 1
            level = abs(level)

        step_time = round((float(ramp_time) / float(level)) / float(0.488))
        if step_time > 31 or step_time < 0:
            step_time = round((float(ramp_time) / float(level)) / float(15.625))
            prescale = 1
        print(">>>>", step_time)

    value = OP_PARAM | (prescale << 14) | (step_time << 9) | (sign << 8) | level
    vh = f"0x{((value & 0xff00) >> 8):02x}"
    vl = f"0x{(value & 0x00ff):02x}"

    return [vh, vl]

def op_wait(labels, inst):
    """
    When a wait instruction is executed, the engine is set in wait status, and
    the PWM values on the outputs are frozen. Note: A wait instruction with
    prescale and time = 0 is invalid and is executed as rst.

    NAME     | VALUE (d) | DESCRIPTION |
    prescale | 0         | Divide master clock (32.7 kHz) by 16 which means 0.488 ms cycle time.
             | 1         | Divide master clock (32.7 kHz) by 512 which means 15.625 ms cycle time.
    time     | 1–31      | Total wait time is = (time) × (prescale). Maximum 484 ms, minimum 0.488 ms.

    """

    OP=0b0000000000000000
    MAX = 484
    MIN = 0.488
    LOW_PRESCALE = 0.488
    HIGH_PRESCALE = 15.625

    try:
        w_time = float(inst['args'][0]) * 1000
    except IndexError as e:
        raise ValueError(f"Missing data [{inst['args']}]")

    if w_time > MAX or w_time < MIN:
        raise ValueError(f"Invalid value [{inst['args']}] valid range is {MAX}ms to {MIN}ms")


    prescale = 0
    value = round(float(w_time) / LOW_PRESCALE)
    if value > 31:
        value = round(float(w_time) / HIGH_PRESCALE)
        prescale = 1

    value = OP | (prescale << 14) | (value << 9)

    vh = f"0x{((value & 0xff00) >> 8):02x}"
    vl = f"0x{(value & 0x00ff):02x}"

    return [vh, vl]


instruction_set = {
    "dw": op_dw,
    "segment": op_nop,
    "map_start": op_nop,
    "load_end":op_nop,
    "map_addr":op_map_addr,
    "map_next":op_nop,
    "map_prev":op_nop,
    "ramp":op_ramp,
    "set_pwm":op_nop,
    "wait":op_wait,
    "branch":op_nop,
    "end":op_nop,
}
