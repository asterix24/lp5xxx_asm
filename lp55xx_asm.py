#!/bin/env python

import re

def op_nop(labels, inst):
    print("NOP")
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

    vh = "0x%02x" % ((value & 0xff00) >> 8)
    vl = "0x%02x" % (value & 0x00ff)

    return [vh, vl]

def op_map_addr(labels, inst):
    #"op":0b100111111, "args_bits":6},
    return []

instruction_set = {
    "dw": op_dw,
    "segment": op_nop,
    "map_start": op_nop,
    "load_end":op_nop,
    "map_addr":op_map_addr,
    "map_next":op_nop,
    "map_prev":op_nop,
    "ramp":op_nop,
    "set_pwm":op_nop,
    "wait":op_nop,
    "branch":op_nop,
    "end":op_nop,
}


def parse(src):
    pc_instruction = 0x0
    labels = {}
    memory = []

    for line in src:
        inst = {
            "addr": pc_instruction,
            "prg": None,
            "op": None,
            "args":[]
        }

        toks = re.split(r"\s+", line)
        inst_args = False
        for tok in toks:
            if inst_args and tok:
                inst["args"].append(tok)
                continue

            label = re.search(r'^\w+:', tok)
            if label is not None:
                if label in labels:
                    raise ValueError("Duplicate label name")

                labels[label.group().replace(":","")] = pc_instruction

            seg = re.search(r"^\.\w+", tok)
            if seg is not None:
                inst['op'] = tok.replace(".", "")
                inst['prg'] = pc_instruction
                inst_args = True

            if tok in instruction_set:
                inst['op'] = tok
                pc_instruction += 1
                inst_args = True

        if label is None and inst['op'] is None:
            continue

        memory.append(inst)

    return memory, labels

def asm(labels, memory):
    asm_bin = []
    for m in memory:
        print(f"{m['addr']:02X}-> {m}")
        data = instruction_set[m['op']](labels, m)
        asm_bin += data

    return asm_bin

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog='lp55xx_asm',
        description='ASM for Texas led driver LP55xx ic',
        epilog='Assemblator for led efx programm')

    parser.add_argument('src_lst')

    args = parser.parse_args()
    print(args.src_lst)

    src = open(args.src_lst)
    memory, labels = parse(src)
    asm_bin = asm(labels, memory)

    for l in labels:
        print(f"{l}: {labels[l]:02X}")

    for n, a in enumerate(asm_bin):
        if not n % 16:
            print()
        print(a, end=", ")


