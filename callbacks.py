#!/bin/env python

def byte_fmt(value):
    vh = f"0x{((value & 0xff00) >> 8):02x}"
    vl = f"0x{(value & 0x00ff):02x}"

    return [vh, vl]

def show_msg(flag, ctx, msg):
    line = "\n\n"
    line += "-" * int((80 - len(flag) - 1) / 2)
    line += f" {flag.upper()} "
    line += "-" * int((80 - len(flag) - 1) / 2)
    line += f"\n-> {ctx['line']}"
    line += f"\n-> line no: {ctx['line_no']}\n"
    line += f"\n{msg}\n\n"
    flag = " Dump "
    line += flag
    line += "-" * int((80 - len(flag) - 1) / 2)
    for i in ["prg", "op", "args"]:
        line += f"\n- {i}: {ctx[i]}"
    line += "\n\n"
    line += "-" * (int((80 - len(flag) - 1) / 2) + len(flag))

    return line

def op_nop(op, table, labels, inst):
    print(f"op_nop: {op}")
    return []

def op_dw(op, table, labels, inst):
    MAX=table[op]["max"]
    MIN=table[op]["min"]

    try:
        value = inst['args'][0]
    except IndexError as e:
        raise ValueError(show_msg("Error", inst, "Missing data"))

    try:
        if "b" in value:
            value = int(value.replace("b",""),2)
        elif "0x" in value:
            value = int(value,16)
        else:
            value = int(value)
    except ValueError as e:
        raise ValueError(show_msg("Error", inst, "Wrong data type"))

    if value > MAX or value < MIN:
        raise ValueError(show_msg("Error", inst, f"Invalid valid range is {MAX} to {MIN}"))

    return byte_fmt(value)

def op_map_addr(op, table, labels, inst):
    """
    The map_addr instruction sets the index pointer to point to the mapping table row
    defined by bits [6:0] and sets the row active. The engine does not push a new PWM
    value to the LED driver output before the set_pwm or ramp instruction is executed.
    If the mapping has been released from an LED, the value in the PWM register still
    controls the LED brightness.

    |NAME         |VALUE (d) |  DESCRIPTION
    |SRAM address | 0–127    | SRAM address containing mapping data restricted to lower half of memory.

    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    try:
        args = inst['args'][0]
    except IndexError as e:
        raise ValueError(show_msg("Error", inst, "Missing arguments"))

    if args not in labels:
        raise ValueError(show_msg("Error", inst, f"No such label found in code"))

    addr = int(labels[args])
    if addr > MAX or addr < MIN:
        raise ValueError(show_msg("Error", inst, "Invalid address"))

    value = OP | addr
    return byte_fmt(value)

def op_ramp(op, table, labels, inst):
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
    OP_PARAM=table[op]['op']
    OP_VAR  =0b1000010000000000
    prescale = 0
    sign = 0
    step_time = 0
    no_increment = 0

    try:
        ramp_time = float(inst['args'][0])
        level = int(inst['args'][1])
    except IndexError as e:
        raise ValueError(show_msg("Error", inst, "Missing arguments"))

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

    value = OP_PARAM | (prescale << 14) | (step_time << 9) | (sign << 8) | level
    return byte_fmt(value)

def op_wait(op, table, labels, inst):
    """
    When a wait instruction is executed, the engine is set in wait status, and
    the PWM values on the outputs are frozen. Note: A wait instruction with
    prescale and time = 0 is invalid and is executed as rst.

    NAME     | VALUE (d) | DESCRIPTION |
    prescale | 0         | Divide master clock (32.7 kHz) by 16 which means 0.488 ms cycle time.
             | 1         | Divide master clock (32.7 kHz) by 512 which means 15.625 ms cycle time.
    time     | 1–31      | Total wait time is = (time) × (prescale). Maximum 484 ms, minimum 0.488 ms.

    """

    OP = table[op]['op']
    MAX = table[op]['max']
    MIN = table[op]['min']
    LOW_PRESCALE = 0.488
    HIGH_PRESCALE = 15.625

    try:
        w_time = float(inst['args'][0]) * 1000
    except IndexError as e:
        raise ValueError(show_msg("Error", inst, "Missing arguments"))

    if w_time > MAX or w_time < MIN:
        raise ValueError(show_msg("Error", inst, f"Invalid valid range is {MAX}ms to {MIN}ms"))


    prescale = 0
    value = round(float(w_time) / LOW_PRESCALE)
    if value > 31:
        value = round(float(w_time) / HIGH_PRESCALE)
        prescale = 1

    value = OP | (prescale << 14) | (value << 9)
    return byte_fmt(value)

def op_load_start(op, table, abels, inst):
    """
    LOAD_START and LOAD_END
    The load_start and load_end instructions define the mapping table locations in SRAM.
    | NAME         | VALUE (d) | DESCRIPTION                                                           |
    | SRAM address | 0–127     | Mapping table start or end address restricted to lower half of memory |
    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    value = 0
    return byte_fmt(value)

def op_load_end(op, table, labels, inst):
    """
    LOAD_START and LOAD_END
    The load_start and load_end instructions define the mapping table locations in SRAM.
    | NAME         | VALUE (d) | DESCRIPTION                                                           |
    | SRAM address | 0–127     | Mapping table start or end address restricted to lower half of memory |
    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    try:
        label = inst['args'][0]
    except IndexError as e:
        raise ValueError(show_msg("Error", inst, "Missing arguments"))

    if not label in labels:
        raise ValueError(show_msg("Error", inst, "No such lable found in source"))

    addr = int(labels[label])
    if addr < MIN or addr > MAX:
        raise ValueError(show_msg("Error", inst, "Wrong address for labels"))


    value = OP | addr
    return byte_fmt(value)

def op_map_start(op, table, labels, inst):
    """
    MAP_START
    The map_start instruction defines the mapping table start address in the
    memory, and the first row of the table is activated (mapped) at the same time.

    | NAME         | VALUE (d) | DESCRIPTION                                                     |
    | SRAM address | 0–127     |  Mapping table start address restricted to lower half of memory.|
    """

    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    try:
        label = inst['args'][0]
    except IndexError as e:
        raise ValueError(show_msg("Error", inst, "Missing arguments"))

    if not label in labels:
        raise ValueError(show_msg("Error", inst, "No such label in source"))

    addr = int(labels[label])
    if addr < MIN or addr > MAX:
        raise ValueError(show_msg("Error", inst, "Wrong address for label"))


    value = OP | addr
    return byte_fmt(value)

def op_map_sel(op, table, labels, inst):
    """
    MAP_SEL
    With the map_sel instruction one, and only one, LED driver can be connected
    to a program execution engine. Connecting multiple LEDs to one engine is
    done with the mapping table. After the mapping has been released from an
    LED, the PWM register value still controls the LED brightness.

    | NAME       | VALUE (d) | DESCRIPTION                               |
    | LED Select | 0–127     | 0 = no drivers selected 1 = LED1 selected |
                             |  2 = LED1 selected                        |
                             |  ...                                      |
                             |  9 = LED9 selected                        |
                             |  10–127 = no drivers selected             |

    """

    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    value = 0
    return byte_fmt(value)

def op_map_clr(op, table, labels, inst):
    """
    MAP_CLR
    The map_clr instruction clears engine-to-driver mapping. After the mapping
    has been released from an LED, the PWM register value still controls the
    LED brightness.
    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    if len(inst['args'] > 0):
        raise ValueError(show_msg("Error", inst, "No arguments needs for this command"))

    value = OP
    return byte_fmt(value)

def op_map_next(op, table, labels, inst):
    """
    MAP_NEXT
    This instruction sets the next row active in the mapping table
    each time it is called. For example, if the second row is active at this
    moment, after the map_next instruction call the third row is active. If the
    mapping table end address is reached, activation rolls to the mapping-table
    start address the next time when the map_next instruction is called. The
    engine does not push a new PWM value to the LED driver output before the
    set_pwm or ramp instruction is executed. If the mapping has been released
    from an LED, the value in the PWM register still controls the LED
    brightness.
    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    if len(inst['args']) > 0:
        raise ValueError(show_msg("Error", inst, "No arguments needs for this command"))

    value = OP
    return byte_fmt(value)

def op_map_prev(op, table, labels, inst):
    """
    MAP_PREV
    This instruction sets the previous row active in the mapping table each time it
    is called. For example, if the third row is active at this moment, after the
    map_prev instruction call the second row is active. If the mapping table start
    address is reached, activation rolls to the mapping table end address next time
    the map_prev instruction is called. The engine does not push a new PWM value to
    the LED driver output before the set_pwm or ramp instruction is executed. If
    the mapping has been released from an LED, the value in the PWM register still
    controls the LED brightness.
    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    if len(inst['args']) > 0:
        raise ValueError(show_msg("Error", inst, "No arguments needs for this command"))

    value = OP
    return byte_fmt(value)

def op_load_next(op, table, labels, inst):
    """
    LOAD_NEXT
    Similar to the map_next instruction with the exception that no mapping is
    set. The index pointer is set to point to the next row and the
    engine-to-LED-driver connection is not updated.

    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    if len(inst['args'] > 0):
        raise ValueError(show_msg("Error", inst, "No arguments needs for this command"))

    value = OP
    return byte_fmt(value)


def op_load_prev(op, table, labels, inst):
    """
    LOAD_PREV
    Similar to the map_prev instruction with the exception that no mapping is
    set. The index pointer is set to point to the previous row and the
    engine-to-LED-driver connection is not updated.
    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    if len(inst['args'] > 0):
        raise ValueError(show_msg("Error", inst, "No arguments needs for this command"))

    value = OP
    return byte_fmt(value)

def op_load_addr(op, table, labels, inst):
    """
    LOAD_ADDR
    The load_addr instruction sets the index pointer to point to the mapping
    table row defined by bits [6:0], but the row is not set active.

    NAME VALUE (d) DESCRIPTION
    | NAME        | VALUE (d) | DESCRIPTION                               |
    | SRAM address| 0–127     | address containing mapping data restricted to lower half of memory|
    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    try:
        args = inst['args'][0]
    except IndexError as e:
        raise ValueError(show_msg("Error", inst, f"Missing arguments"))

    if args not in labels:
        raise ValueError(show_msg("Error", inst, f"No such label found in code"))

    addr = int(labels[args])
    if addr > MAX or addr < MIN:
        raise ValueError(show_msg("Error", inst, f"Invalid address"))

    value = OP | addr
    return byte_fmt(value)

def op_set_pwm(op, table, labels, inst):
    """
    Set_PWM
    This instruction is used for setting the PWM value on outputs LED0 to LED8
    without any ramps. Set the PWM output value from 0 to 255 with PWM value
    bits [7:0]. Instruction execution takes 16 32-kHz clock cycles (= 488 μs).

    NAME VALUE (d) DESCRIPTION
    | NAME        | VALUE (d) | DESCRIPTION                               |
    | PWM value   | 0–255     |PWM output duty cycle 0–100%
    | variable    | 0-3       | 0 = local variable A
    |             |           | 1 = local variable B
    |             |           | 2 = global variable C
    |             |           | 3 = global variable D


    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    try:
        level = inst['args'][0]
        level = int(level)
    except IndexError as e:
        raise ValueError(show_msg("Error", inst, f"Missing arguments"))
    except ValueError as e:
        raise ValueError(show_msg("Error", inst, f"Wrong data type, int needed"))

    if level < MIN or level > MAX:
        raise ValueError(show_msg("Error", inst, f"Invalid valid range is {MAX} to {MIN}"))

    value = OP | level
    return byte_fmt(value)

def op_end(op, table, labels, inst):
    """
    END
    End program execution. The instruction takes 16 32-kHz clock cycles.

    | NAME  | VALUE (d) | DESCRIPTION
    | int   | 0         | No interrupt is sent. PWM register values remain intact.
    |       | 1         | Reset program counter value to 0 and send interrupt to
    |       |           | processor by pulling the INT pin down and setting the corresponding status
    |       |           | bit high to notify that the program has ended. PWM register values remain
    |       |           | intact. Interrupts can be cleared by reading the interrupt bits in
    |       |           | STATUS/INTERRUPT register at address 3Ch.
    | reset | 0         | Reset program counter value to 0 and hold. PWM register values remain intact.
    |       | 1         | Reset program counter value to 0 and hold. PWM register values of the
    |       |           | non-mapped drivers remain. PWM register values of the mapped drivers are set to
    |       |           |  0000 0000b.
    """

    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    i = 0
    r = 0

    for a in inst['args']:
        if "i" in a.lower():
            i = 1
        if "r" in a.lower():
            r = 1
        if not a.lower() in ['i', 'r']:
            raise ValueError(show_msg("Error", inst, f"Wrong arguments valid are [i, r]"))

    value = OP | i << 12 | r << 11
    return byte_fmt(value)

def op_reset(op, table, labels, inst):
    """
    RST
    The rst instruction resets the program counter register (address 30h, 31h, or
    32h) and continues executing the program from the program the start address
    defined in register addresses 4Bh–4Dh. The instruction takes 16 32‐kHz clock
    cycles. Note that default value for all program memory registers is 0000h,
    which is the rst instruction.
    """

    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    if len(inst['args']) > 0:
        raise ValueError(f"No arguments needs for this command {inst}")

    value = OP
    return byte_fmt(value)

def op_int(op, table, labels, inst):
    """
    INT
    Send an interrupt to the processor by pulling the INT pin down and setting the
    corresponding status bit high. Interrupts can be cleared by reading the
    interrupt bits in the ENGINE_STATUS register at address 3Ch.

    """

    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    if len(inst['args']) > 0:
        raise ValueError(f"No arguments needs for this command {inst}")

    value = OP
    return byte_fmt(value)

def op_branch(op, table, labels, inst):
    """
    BRANCH
    The branch instruction is provided for repeating a portion of the program
    code several times. The branch instruction loads a step number value to the
    program counter. A loop count parameter defines how many times the
    instructions inside the loop are repeated. The step number is loaded into
    the PC when the instruction is executed. The PC is relative to the
    ENGINEx_PROG_START register setting. The LP5569 device supports nested
    looping, that is, a loop inside a loop. The number of nested loops is not
    limited. The instruction takes 16 32-kHz clock cycles.

    | NAME        | VALUE (d) | DESCRIPTION
    | loop count  | 0-63      | The number of loops to be done. 0 means an infinite loop
    | step number | 0-127     | The step number to be loaded to program counter.
    | loop count  | 0-3       | Selects the variable for loop count value. Loop
    |             |           | count is loaded with the value of the variable defined below.
    |             |           | 0 = Local variable A
    |             |           | 1 = Local variable B
    |             |           | 2 = Global variable C
    |             |           | 3 = Global variable D

    """
    OP=table[op]['op']
    MIN=table[op]['min']
    MAX=table[op]['max']

    try:
        nloops = int(inst['args'][0])
        nsteps = inst['args'][1]
    except IndexError as e:
        raise ValueError(show_msg("Error", inst, f"Missing arguments"))
    except ValueError as e:
        raise ValueError(show_msg("Error", inst, f"Wrong data type"))

    if nsteps not in labels:
        raise ValueError(show_msg("Error", inst, f"No such label found in code"))

    addr = int(labels[nsteps]) - int(inst['prg'])
    if addr > MAX[1] or addr < MIN[1]:
        raise ValueError(show_msg("Error", inst, f"Invalid valid range is {MAX} to {MIN}"))

    if nloops < MIN[0] or nloops > MAX[0]:
        raise ValueError(show_msg("Error", inst, f"Invalid valid range is {MAX} to {MIN}"))

    value = OP | nloops << 7 | addr
    return byte_fmt(value)

