#!/bin/env python


from callbacks import op_dw, op_nop, op_wait
from callbacks import op_load_start, op_load_end, op_load_next, op_load_prev, op_load_addr, op_map_addr
from callbacks import op_map_start, op_map_sel, op_map_clr, op_map_next, op_map_prev
from callbacks import op_ramp, op_set_pwm
from callbacks import op_reset, op_end, op_int, op_branch, op_trigger, op_trig_clear
from callbacks import op_jne, op_jl, op_jge, op_je
from callbacks import op_ld, op_add, op_sub


lookup_table = {
    "dw":         {"callback": op_dw,         "mask": 0x0000, "op": None, "min": 0, "max": 0x1ff},
    "segment":    {"callback": op_nop,        "mask": 0x0000, "op": None, "min": None, "max": None},

    "load_start": {"callback": op_load_start, "mask": 0x003F, "op": 0b1001111000000000,  "min": 0, "max": 127},
    "map_start":  {"callback": op_map_start,  "mask": 0x003F, "op": 0b1001110000000000,  "min": 0, "max": 127},
    "load_end":   {"callback": op_load_end,   "mask": 0x003F, "op": 0b1001110010000000,  "min": 0, "max": 127},
    "map_sel":    {"callback": op_map_sel,    "mask": 0x003F, "op": 0b1001110100000000,  "min": 0, "max": 127},
    "map_clr":    {"callback": op_map_clr,    "mask": 0x0000, "op": 0b1001110100000000,  "min": None, "max": None},
    "map_next":   {"callback": op_map_next,   "mask": 0x0000, "op": 0b1001110110000000,  "min": None, "max": None},
    "map_prev":   {"callback": op_map_prev,   "mask": 0x0000, "op": 0b1001110111000000,  "min": None, "max": None},
    "load_next":  {"callback": op_load_next,  "mask": 0x0000, "op": 0b1001110110000001,  "min": None, "max": None},
    "load_prev":  {"callback": op_load_prev,  "mask": 0x0000, "op": 0b1001110111000001,  "min": None, "max": None},
    "load_addr":  {"callback": op_load_addr,  "mask": 0x003F, "op": 0b1001111100000000,  "min": 0, "max": 127},
    "map_addr":   {"callback": op_map_addr,   "mask": 0x003F, "op": 0b1001111110000000,  "min": 0, "max": 127},

    "ramp":       {"callback": op_ramp,       "mask": 0x7FFF, "op": 0b0000000000000000,  "min": None, "max": None,
                                             "maskv": 0x001F,"opv": 0b1000010000000000,  "minv": None, "maxv": None},
    "set_pwm":    {"callback": op_set_pwm,    "mask": 0x00FF, "op": 0b0100000000000000,  "min": 0, "max": 255,
                                             "maskv": 0x0003,"opv": 0b1000010001100000, "minv": None, "maxv": None},
    "wait":       {"callback": op_wait,       "mask": 0x7E00, "op": 0b0000000000000000,  "min": 0.488, "max": 484},

    "rst":        {"callback": op_reset,      "mask": 0x0000, "op": 0b0000000000000000,  "min": None, "max": None},
    "end":        {"callback": op_end,        "mask": 0x1800, "op": 0b1100000000000000,  "min": None, "max": None},
    "int":        {"callback": op_int,        "mask": 0x0000, "op": 0b1100010000000000,  "min": None, "max": None},
    "branch":     {"callback": op_branch,     "mask": 0x3FFF, "op": 0b1010000000000000,  "min": [0, 0], "max": [63, 127],
                                             "maskv": 0x01FF,"opv": 0b1000011000000000, "minv": None, "maxv": None},
    "trigger":    {"callback": op_trigger,    "mask": 0x1FFE, "op": 0b1110000000000000,  "min": 0, "max": 31},
    "trig_clear": {"callback": op_trig_clear, "mask": 0x0000, "op": 0b1110000000000000,  "min": None, "max": None},

    "jne":        {"callback": op_jne,        "mask": 0x01FF, "op": 0b1000100000000000,  "min": 0, "max": 31},
    "jl":         {"callback": op_jl,         "mask": 0x01FF, "op": 0b1000101000000000,  "min": 0, "max": 31},
    "jge":        {"callback": op_jge,        "mask": 0x01FF, "op": 0b1000110000000000,  "min": 0, "max": 31},
    "je":         {"callback": op_je,         "mask": 0x01FF, "op": 0b1000111000000000,  "min": 0, "max": 31},

    "ld":         {"callback": op_ld,         "mask": 0x0CFF, "op": 0b1001000000000000,  "min": [0, 0], "max": [2, 255]},
    "add":        {"callback": op_add,        "mask": 0x0CFF, "op": 0b1001000100000000,  "min": [0, 0], "max": [2, 255],
                                             "maskv": 0x0C0F,"opv": 0b1001001100000000, "minv": [0, 0], "maxv": [3, 3]},
    "sub":        {"callback": op_sub,        "mask": 0x0CFF, "op": 0b1001001000000000,  "min": [0, 0], "max": [2, 255],
                                             "maskv": 0x0C0F,"opv": 0b1001001100010000, "minv": [0, 0], "maxv": [3, 3]},
}


"""
"load_start":  : 0b1001111000000000,
"map_start":   : 0b1001110000000000,
"load_end":    : 0b1001110010000000,
"map_sel":     : 0b1001110100000000,
"map_clr":     : 0b1001110100000000,
"map_next":    : 0b1001110110000000,
"map_prev":    : 0b1001110111000000,
"load_next":   : 0b1001110110000001,
"load_prev":   : 0b1001110111000001,
"load_addr":   : 0b1001111100000000,
"map_addr":    : 0b1001111110000000,
"ramp":        : 0b0000000000000000,
               : 0b1000010000000000,
"set_pwm":     : 0b0100000000000000,
               : 0b1000010001100000,
"wait":        : 0b0000000000000000,
"rst":         : 0b0000000000000000,
"end":         : 0b1100000000000000,
"int":         : 0b1100010000000000,
"branch":      : 0b1010000000000000,
"trigger":     : 0b1110000000000000,
"trig_clear":  : 0b1110000000000000,
"jne":         : 0b1000100000000000,
"jl":          : 0b1000101000000000,
"jge":         : 0b1000110000000000,
"je":          : 0b1000111000000000,
"ld":          : 0b1001000000000000,
"add":         : 0b1001000100000000,
               : 0b1001001100000000,
"sub":         : 0b1001001000000000,
               : 0b1001001100010000,
"""

