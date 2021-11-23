# PROGRAM UTAMA PARSER

'''
Alur umum dari program yang akan dibangun adalah sebagai berikut.
    1. Menerima input berupa file eksternal berisi string yang merupakan kode sebuah program python
    2. Melakukan evaluasi sintaks dengan CFG
    3. Melakukan evaluasi nama-nama variabel yang ada dengan FA
    4. Memberikan keluaran hasil evaluasi program antara “Accepted” jika input diterima atau “Syntax Error” jika input tidak diterima
    5. (BONUS) Memberi tahu letak dan detail kesalahan syntax jika ada 
'''

import sys
from CFGtoCNF import CFGtoCNF
from CNFtoCNFdict import CNFtoCNFdict
from CYK import CYK
from FA import isVarValid
from tokenizer import tokenizer

# KAMUS
listReservedNonTerminal = ['IF', 'ELSE', 'ELIF', 'DEF', 'CLASS', 'FOR', 'WHILE', 'BREAK', 'PASS', 'CONTINUE', 'RETURN', 'TRIPLEDOUBLEQUOTEOPEN','TRIPLEDOUBLEQUOTECLOSE', 'TRIPLESINGLEQUOTEOPEN', 'TIPLESINGLEQUOTECLOSE']
stack = []
isValid = True


def cleanIfForWhile(stack):
    while stack:
            prevStack = stack
            if stack[-1][0] == 'IF':
                stack.pop()
            if stack[-1][0] == 'FOR' :
                stack.pop()
            if stack[-1][0] == 'WHILE':
                stack.pop()
            # kalau sudah gada perubahan di stack
            if prevStack == stack: 
                break
    return stack
# ALGORITMA

'''1. Menerima input berupa file eksternal berisi string yang merupakan kode sebuah program python'''

nama_file = sys.argv[1]
with open(nama_file,"r") as f:
    data = f.read()

# input disimpan dalam var 'data'

'''2. Melakukan evaluasi sintaks dengan CFG'''
# melakukan print jika terjadi kesalahan. implementasi dari Stack terjadi disini.

# siap kan CFG hingga menjadi CNFdict
print("translating CFG to CNF...")
CFGtoCNF("cfg.txt")
print("translating CNF to CNF dictionary...")
CNFdict = CNFtoCNFdict()
print("start parsing...")
listDataLine = data.split("\n")
baris = 0
mustFollowedByS = True
for eachListDataLine in listDataLine:
    baris += 1
    # bersihkan tabulasi dan spasi
    eachListDataLine = eachListDataLine.lstrip().rstrip()
    if(eachListDataLine != ""):
        tokenizedLine = tokenizer(eachListDataLine)
        
        listTopCNF = CYK(tokenizedLine,CNFdict)

        # kalau di dalam listTopCNF itu gada S dan ada ReservedNonTerminal, brarti perlu tindakan khusus dengan stack
        isSpecial = False
        adaS = False
        specialNonTerminal = ''
        # untuk mencatat apakkah sebelumnya sudah ada Statement. untuk menghandle 'if diikuti else tapi belom ada statement, atau def tanpa statement
        # print("listTopCNF")
        # print(listTopCNF)
        for eachTopCNF in listTopCNF:
            if eachTopCNF == 'S':
                adaS = True
                mustFollowedByS = False
                break
            else:
                for eachReservedNonTerminal in listReservedNonTerminal:
                    if eachTopCNF == eachReservedNonTerminal:
                        # kasus khusus, hopefully doesnt kick my ass later
                        if 'TRIPLEDOUBLEQUOTECLOSE' in listTopCNF:
                            exists = False
                            for element in stack:
                                if element[0] == 'TRIPLEDOUBLEQUOTEOPEN':
                                    exists = True
                                    break
                                specialNonTerminal = 'TRIPLEDOUBLEQUOTECLOSE'
                            else:
                                specialNonTerminal = 'TRIPLEDOUBLEQUOTECOPEN'
                        elif 'TRIPLESINGLEQUOTECLOSE' in listTopCNF:
                            exists = False
                            for element in stack:
                                if element[0] == 'TRIPLESINGLEQUOTEOPEN':
                                    exists = True
                                    break
                            if exists:
                                specialNonTerminal = 'TRIPLESINGLEQUOTECLOSE'
                            else:
                                specialNonTerminal = 'TRIPLESINGLEQUOTEOPEN'
                        else:
                            specialNonTerminal = eachTopCNF
                        isSpecial = True
                        
                        break
            if isSpecial or adaS:
                break
        
        if(isSpecial and not(adaS)):
            # kalo nge append, yang aku append cuman yg special. ini bakal trouble kalo suatu statement bisa menjadi 2 spesial yang berbeda(misal dia IF statement sekaligus ELSE, tapi dia bukan S), tapi keknya gk mungkin. jadi harusnya aman 
            # print("specialNonTerminal")
            # print(specialNonTerminal)
            # print("stack")
            # print(stack)
            if specialNonTerminal == 'IF':
                mustFollowedByS = True
                stack.append(specialNonTerminal)
            elif specialNonTerminal == 'ELSE':
                if mustFollowedByS:
                    isValid = False
                if (len(stack) != 0 and stack[-1] == 'IF'): # stack[-1] artinya top of stack.
                    stack.pop()
                else:
                    # print("ada else tapi atasnya bukan if")
                    isValid = False
        
            elif specialNonTerminal == 'ELIF':
                if mustFollowedByS:
                    isValid = False
                if not(len(stack) != 0 and stack[-1] == 'IF'): # stack[-1] artinya top of stack.
                    print("ada elif tanpa if")
                    isValid = False
               
            elif specialNonTerminal == 'DEF':
                mustFollowedByS = True
                stack.append((specialNonTerminal,baris))
                
            elif specialNonTerminal == 'CLASS':
                mustFollowedByS = True
                stack.append((specialNonTerminal,baris))
               
            elif specialNonTerminal == 'FOR':
                mustFollowedByS = True
                stack.append((specialNonTerminal,baris))
             
            elif specialNonTerminal == 'WHILE':
                mustFollowedByS = True
                stack.append((specialNonTerminal,baris))
          
            elif specialNonTerminal == 'BREAK':
                mustFollowedByS = False
                
                if (len(stack) != 0 and (stack[-1][0] == 'FOR' or stack[-1][0] == 'WHILE')):
                    stack.pop()
                else:
                    isValid = False
            elif specialNonTerminal == 'PASS':
                mustFollowedByS = False
                
                if (len(stack) != 0 and (stack[-1][0] == 'FOR' or stack[-1][0] == 'WHILE')):
                    stack.pop()
                else:
                    isValid = False
            elif specialNonTerminal == 'CONTINUE':
                mustFollowedByS = False
                
            elif specialNonTerminal == 'RETURN':
                print("return!")
                mustFollowedByS = False
                stack = cleanIfForWhile(stack)
                if (len(stack) != 0 and stack[-1][0] == 'DEF'):
                    stack.pop()
                elif(len(stack) != 0 and 'DEF' in stack):
                    pass
                else:
                    isValid = False
            elif specialNonTerminal == 'TRIPLEDOUBLEQUOTECLOSE':
                if (len(stack) != 0 and stack[-1][0] == 'TRIPLEDOUBLEQUOTEOPEN'):
                    stack.pop()
                else:
                    isValid = False
            elif specialNonTerminal == 'TRIPLEDOUBLEQUOTEOPEN':
                stack.append((specialNonTerminal, baris))
            elif specialNonTerminal == 'TRIPLESINGLEQUOTECLOSE':
                if (len(stack) != 0 and stack[-1][0] == 'TRIPLESINGLEQUOTEOPEN'):
                    stack.pop()
                else:
                    isValid = False
            elif specialNonTerminal == 'TRIPLESINGLEQUOTEOPEN':
                stack.append((specialNonTerminal, baris))
                
        elif 'TRIPLESINGLEQUOTEOPEN' in stack or 'TRIPLEDOUBLEQUOTEOPEN' in stack:
            continue    
        elif(not(isSpecial) and not(adaS)): # berarti ada baris yang gk valid
            isValid = False
            # print("ada baris yang tidak valid:")
            # print(eachListDataLine)
        # kalo udah ada baris yang gk valid, gk usah cek bawah2nya
        if not(isValid):
            break
# checking tiap line selesai. 
print("==============================")
print("parsing done")
if not(isValid):
    print("\n!!!!! NOT VALID !!!!!\n")
    print("baris yang dicurigai")
    print(eachListDataLine)
    if stack:
        print("yang berada di dalam")
        for element in stack:
            print(element[0], "(baris " + str(element[1]) + ")")
    
# bersihin stack, ada keyword yang gk perlu penutup (contoh IF)
if isValid:
    print("kondisi stack")
    print(stack)
    while stack:
        prevStack = stack
        if stack[-1][0] == 'IF' and not mustFollowedByS:
            stack.pop()
        elif stack[-1][0] == 'DEF' and not mustFollowedByS:
            stack.pop()
        elif stack[-1][0] == 'FOR' and not mustFollowedByS:
            stack.pop()
        elif stack[-1][0] == 'WHILE' and not mustFollowedByS:
            stack.pop()
        # kalau sudah gada perubahan di stack
        if prevStack == stack: 
            break
        # if2 lainnya
    

# Stack harus kosong. kalau gk kosong berarti gk valid
    print("KONDISI STACK STELAH DIBERSIHKAN")
    print(stack)
    if stack: # jika semua line aman, tapi stack masih ada isinya
        print("stack tidak kosong.")
        print("ada ", stack[-1][0], "tanpa penutup")
    else:
        print("\n!!!!! yay valid !!!!!!\n")