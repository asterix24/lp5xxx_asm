#!/bin/env python

from callbacks import *

lookup_table = {
"dw":        { "callback":op_dw,      "op":None, "min":0, "max":0x1ff},

"load_start":{ "callback":op_load_start,"op":0b1001111000000000, "min":0, "max":127},
"map_start": { "callback":op_map_start, "op":0b1001110000000000, "min":0, "max":127},
"load_end":  { "callback":op_load_end,  "op":0b1001110010000000, "min":0, "max":127},
"map_sel":   { "callback":op_map_sel,   "op":0b1001110100000000, "min":0, "max":127},
"map_clr":   { "callback":op_nop,       "op":0b1001110100000000, "min":None, "max":None},
"map_next":  { "callback":op_nop,       "op":0b1001110110000000, "min":None, "max":None},
"map_prev":  { "callback":op_nop,       "op":0b1001110110000000, "min":None, "max":None},
"load_next": { "callback":op_nop,       "op":0b1001110110000000, "min":None, "max":None},
"load_prev": { "callback":op_nop,       "op":0b1001110110000000, "min":None, "max":None},
"load_addr": { "callback":op_nop,       "op":0b1001111100000000, "min":None, "max":None},
"map_addr":  { "callback":op_map_addr,  "op":0b1001111110000000, "min":0, "max":127},

"ramp":      { "callback":op_ramp,      "op":0b0000000000000000, "min":None, "max":None},
"set_pwm":   { "callback":op_set_pwm,   "op":0b0100000000000000, "min":0, "max":255},

"wait":      { "callback":op_wait,    "op":0x0, "min":0.488, "max":484},

"branch":    { "callback":op_nop,     "op":None, "min":None, "max":None},
"end":       { "callback":op_nop,     "op":None, "min":None, "max":None},

"segment":   { "callback":op_nop,     "op":None, "min":None, "max":None},
}
