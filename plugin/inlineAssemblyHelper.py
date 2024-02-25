from __future__ import print_function

import idautils
import idc
import ida_idaapi
import ida_hexrays
import ida_lines
import re

from inline_assembly.instruction import instruction_dict
from inline_assembly.instruction_updater import scrape_instructions

class inline_assembly_hooks_t(ida_hexrays.Hexrays_Hooks):
    def func_printed(self, cfunc):
        inside_asm_block = False
        added_comments = set()

        for sl in cfunc.get_pseudocode():
            if "__asm" in sl.line:
                inside_asm_block = True

            if inside_asm_block:
                
                matches = re.finditer(r'\b([a-zA-Z_]\w*)\b', sl.line)                
                for match in matches:
                    instruction = match.group(1)
                    if instruction == "__asm":
                        continue
                    else:
                        clean_instruction_ = instruction

                        for mnemonic, definition in instruction_dict.items():
                            if clean_instruction_ == mnemonic or clean_instruction_[1:] == mnemonic:
                                if mnemonic not in added_comments:
                                    sl.line += f" // {definition}"
                                    added_comments.add(mnemonic)
                                    break
                        

                if "}" in sl.line:
                    inside_asm_block = False

        return 0

class inlineAssembly(ida_idaapi.plugin_t):
    flags = ida_idaapi.PLUGIN_HIDE
    wanted_name = "Hex-Rays Inline Assembly Helper (IDAPython)"
    wanted_hotkey = ""
    comment = "An IDAPython plugin that adds a comment for inline assembly"
    help = ""

    def init(self):
        if ida_hexrays.init_hexrays_plugin():
            scrape_instructions()
            self.inline_assembly_hooks = inline_assembly_hooks_t()
            self.inline_assembly_hooks.hook()
            print("[InlineAssembly] Loaded plugin v0.0.0.1 -- Made with love by @0xdeadc0de___")
            return ida_idaapi.PLUGIN_KEEP

    def term(self):
        self.inline_assembly_hooks.unhook()

    def run(self, arg):
        pass

def PLUGIN_ENTRY():
    return inlineAssembly()
