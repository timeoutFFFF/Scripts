"""
Used to decode XOR obuscated strings in Psorophora
File hash: ea81fcae0255a84a8a2a6fb19e46eda9a0960886e645497a8139aa47c101dafa
"""

import ida_bytes, idautils

def add_comment(ea, comment, flag=False):
    ida_bytes.append_cmt(ea, comment, flag)
    

def xor_inst(ea, disasm):
    # Get first asn second operands
    first_op_type = idc.get_operand_type(ea,0)
    second_op_type = idc.get_operand_type(ea,1)
  
    # https://www.hex-rays.com/products/ida/support/idadoc/276.shtml
    # 2 = o_meme
    # 5 = o_imm
    if (second_op_type == 5) and (first_op_type == 2):
        
        # get the first and second operand values
        first_op_value = idc.get_operand_value(ea, 0)
        second_op_value = idc.get_operand_value(ea, 1)
        
      
        if second_op_value > 0xFF:
            print(f"{ea:0X} => {disasm}")
            first_op_bytes = idaapi.get_bytes(first_op_value, 4)
            result = int.from_bytes(first_op_bytes,'big') ^ second_op_value
            
            # not added as comment, the result doesn't contain UTF-8 
            # encoded string
            print(result.to_bytes((result.bit_length()+7)//8,'big'))
        
            #print(result)
            #print(f"{first_byte:0X}^{second_op_value:0X}={result:0X}; {chr(result)}")
        else:
            first_op_byte = idaapi.get_byte(first_op_value)
            result = first_op_byte ^ second_op_value
            add_comment(ea, chr(result) )
        
        
       
def iter_all_functions():
    
    # Get all the functions present in file
    for funcEA in idautils.Functions():
        flags = idc.get_func_flags(funcEA)
        if flags & FUNC_LIB or flags & FUNC_THUNK:
            continue

        dism_addr = list(idautils.FuncItems(funcEA))
        
        for i in range(len(dism_addr)):
            disasm = idc.generate_disasm_line(dism_addr[i],0)
            if 'xor' in disasm:
                xor_inst(dism_addr[i], disasm)
              

iter_all_functions()

