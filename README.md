# Assembler for Texas IC Led Driver Family LP5569

![Unittest](https://github.com/asterix24/lp5xxx_asm/actions/workflows/python-app.yml/badge.svg)

## Description

The LP5569 device is a programmable, easy-to-use 9-channel I2C LED driver designed to produce lighting effects for various applications. The LED driver is equipped with an internal SRAM memory for user- programmed sequences and three programmable LED engines, which allow operation without processor control. Autonomous operation reduces system power consumption when the processor is put in sleep mode.

<img width="805" alt="immagine" src="https://github.com/asterix24/lp5xxx_asm/assets/1128161/76ae880c-de6d-4089-95f0-fcccb92c2b42">

Creating of the lighting effect is done by writing a program to run in the devices, this should be done manually and traduce it in binary sequence. TI provides a software tool that can be used with the Eva board to control and help develop lighting effects by writing assembly code.

<img width="1216" alt="immagine" src="https://github.com/asterix24/lp5xxx_asm/assets/1128161/66f29e1e-9d4b-4ee3-976d-93c0a6956cd1">

The tool is complete, but it is a GUI for the developed kit, so it only runs in Windows and is quite limited in text editing.

So, I decided to write my asm tools that allow you to write down an asm application with your favorite text editor and to run it everywhere.

## Feature

The assembly is written in Python for ease of use on all platforms and fast development. To check if the generated binary is correct, I use ase reference to the binary generated by the EVA GUI tools, and I tested it on 2 lp5569 connected in to the same bus.

Now the feature are:
- fully comply with all instructions set 
- all src for lp5569 could be assembled
- generate the same hex file
- generate the .c and .h source file to link in your c procjec
- cli inteface
- clear error messages

## What next?

- Write a deassembler from the bin and program index.
- asm code analisys
- Implement a meta-language to make pattern development easier
- Simulator

# Usage

The asm uses standard Python3 without any dependencies.
In the `src` folder you could find some example of asm that we use in the unittest.

<img width="672" alt="immagine" src="https://github.com/asterix24/lp5xxx_asm/assets/1128161/3f71dc1a-6676-4ec3-9de6-25c8490cbf8d">

To assemble src, you just do this:
```
~/src/github/ti_lp55xx_asm · (main ±)
➜  python lp5xxx_asm.py src/test1.src   
```
By default the output is `hex` file.

<img width="681" alt="immagine" src="https://github.com/asterix24/lp5xxx_asm/assets/1128161/506ea6f7-7776-4a8b-b245-67a6dea8f7d3">

If you want to generate also a .c .h source file as well:

<img width="640" alt="immagine" src="https://github.com/asterix24/lp5xxx_asm/assets/1128161/54d7003b-3b08-48d3-9dc6-4b18f68f6ba7">

<img width="638" alt="immagine" src="https://github.com/asterix24/lp5xxx_asm/assets/1128161/a6cdd710-9e8b-4fae-8f2c-380cea7f3937">

If you want overwrite the default output filename, you can specify manually specify the .c and .h name with its path:

<img width="620" alt="immagine" src="https://github.com/asterix24/lp5xxx_asm/assets/1128161/0bd42fe4-c678-4baa-86e4-37b9f58debe7">

There is the possibility to build more src files at the same time, the output will be one hex file for each source file you would build. If you specify the `-c` switch to build source files, the behavior is the same. But if you specify the `-o` switch to overwrite the default output, all sources will be merged into the given filename

# Disclaimer

This software is distributed under the terms of the GNU General Public License Version 2 (GPL2) without any warranty, expressed or implied. The software is provided "as is," and the user assumes the entire risk as to the quality and performance of the software. The developers and contributors to this software shall not be held liable for any damages or issues arising from the use or inability to use this software, including but not limited to direct, indirect, incidental, or consequential damages.

The software may not function as intended under all circumstances, and its suitability for any specific purpose cannot be guaranteed. Users are encouraged to use this software at their own discretion and are responsible for testing, verifying, and ensuring its appropriateness for their use case.

By using this software, you acknowledge and agree that no guarantees or warranties, explicit or implied, have been made by the developers, contributors, or distributors regarding its performance, reliability, or fitness for any particular purpose.

Please carefully read and understand the terms of the GPL2 license under which this software is distributed. Your use of this software implies your acceptance of these terms and conditions.

This disclaimer helps to clarify the lack of warranty and limitations of liability associated with the software while emphasizing the user's responsibility to assess its suitability for their needs.


