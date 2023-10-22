#!/bin/env python

from callbacks import *

lookup_table = {
"dw":        { "callback":op_dw,      "op":None, "min":0, "max":0x1ff},

"load_start":{ "callback":op_load_start,"op":0b1001111000000000, "min":0, "max":127},
"map_start": { "callback":op_map_start, "op":0b1001110000000000, "min":0, "max":127},
"load_end":  { "callback":op_load_end,  "op":0b1001110010000000, "min":0, "max":127},
"map_sel":   { "callback":op_map_sel,   "op":0b1001110100000000, "min":0, "max":127},
"map_clr":   { "callback":op_map_clr,   "op":0b1001110100000000, "min":None, "max":None},
"map_next":  { "callback":op_map_next,  "op":0b1001110110000000, "min":None, "max":None},
"map_prev":  { "callback":op_map_prev,  "op":0b1001110111000000, "min":None, "max":None},
"load_next": { "callback":op_load_next, "op":0b1001110110000001, "min":None, "max":None},
"load_prev": { "callback":op_load_prev, "op":0b1001110111000001, "min":None, "max":None},
"load_addr": { "callback":op_load_addr, "op":0b1001111100000000, "min":0, "max":127},
"map_addr":  { "callback":op_map_addr,  "op":0b1001111110000000, "min":0, "max":127},

"ramp":      { "callback":op_ramp,      "op":0b0000000000000000, "min":None, "max":None,
                                       "opv":0b1000010000000000,"minv":None,"maxv":None},
"set_pwm":   { "callback":op_set_pwm,   "op":0b0100000000000000, "min":0, "max":255,
                                       "opv":0b1000010001100000,"minv":None,"maxv":None},
"wait":      { "callback":op_wait,      "op":0b0000000000000000, "min":0.488, "max":484},

"rst":       { "callback":op_reset,     "op":0b0000000000000000, "min":None, "max":None},
"end":       { "callback":op_end,       "op":0b1100000000000000, "min":None, "max":None},
"int":       { "callback":op_int,       "op":0b1100010000000000, "min":None, "max":None},
"branch":    { "callback":op_branch,    "op":0b1010000000000000, "min":[0,0], "max":[63, 127]},

"trigger":   { "callback":op_trigger,   "op":0b1110000000000000, "min":0, "max":31},
"trig_clear":{ "callback":op_trig_clear,"op":0b1110000000000000, "min":None, "max":None},

"jne":       { "callback":op_jne,       "op":0b1000100000000000, "min":0, "max":31},
"jl":        { "callback":op_jl,        "op":0b1000101000000000, "min":0, "max":31},
"jge":       { "callback":op_jge,       "op":0b1000110000000000, "min":0, "max":31},
"je":        { "callback":op_je,        "op":0b1000111000000000, "min":0, "max":31},

"ld":        { "callback":op_ld,        "op":0b1001000000000000, "min":[0,0], "max":[2,255]},
"add":       { "callback":op_add,       "op":0b1001000100000000, "min":[0,0], "max":[2,255],
                                       "opv":0b1001001100000000,"minv":[0,0],"maxv":[3,3]},
"sub":       { "callback":op_sub,       "op":0b1001001000000000, "min":[0,0], "max":[2,255],
                                       "opv":0b1001001100010000,"minv":[0,0],"maxv":[3,3]},

"segment":   { "callback":op_nop,     "op":None, "min":None, "max":None},
}

