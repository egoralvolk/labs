from Scanner import *
from nonterminal_for_LL1 import *
from Tree import *
from stack import *
from list import List
from procedures_for_sup import *


class Variable:
    type_ = 0
    value = 0
    name = ''
    id_struct = None


def ll1(sc: TScanner):
    def epsilon():
        magazine.pop()

    magazine = Stack()
    triads = List()
    tree = Node()
    tree.set_current(tree)
    set_scanner(sc)
    v0 = 0
    fl = 1
    stack_for_ifs = Stack()
    operands = Stack()
    operations = Stack()
    current_variable = Variable()
    magazine.push(TEnd)
    magazine.push(neterm_Program)
    lex, t = sc.scan()

    while fl == 1:
        if magazine.get_top() < MinTypeTerminal:
            if magazine.get_top() == t:
                if t == TEnd:
                    fl = 0
                else:
                    lex, t = sc.scan()
                    magazine.pop()
            else:
                sc.print_error("Ожидался символ", lex)
        else:
            if magazine.get_top() == neterm_Program:
                magazine.pop()
                if t == TEnd:
                    epsilon()
                    break
                else:
                    magazine.push(neterm_Program)
                    magazine.push(neterm_Description)
                    current_variable.id_struct = None

            elif magazine.get_top() == neterm_Description:
                magazine.pop()
                if t == TStruct:
                    magazine.push(neterm_Struct)
                    current_variable.type_ = DATA_TYPE.index('TYPE_STRUCT')
                    current_variable.is_struct = True
                elif t == TShort:
                    uk = sc.get_uk()
                    lex1, t1 = sc.scan()
                    lex2, t2 = sc.scan()
                    sc.put_uk(uk)
                    if t1 == TInt:
                        if t2 == TMain:
                            magazine.push(neterm_Main)
                            current_variable.type_ = DATA_TYPE.index('TYPE_MAIN')
                        else:
                            magazine.push(TSemicolon)
                            magazine.push(neterm_ListOfVariables)
                            magazine.push(neterm_Type)
                            current_variable.type_ = DATA_TYPE.index('TYPE_SHORT_INT')
                    else:
                        sc.print_error("Ошибка, ожидался", "int")
                    del lex1, lex2, t1, t2, uk
                else:
                    magazine.push(TSemicolon)
                    magazine.push(neterm_ListOfVariables)
                    magazine.push(neterm_Type)
                    if t == TDouble:
                        current_variable.type_ = DATA_TYPE.index('TYPE_DOUBLE')
                    else:
                        current_variable.type_ = DATA_TYPE.index('TYPE_STRUCT')
                        current_variable.id_struct = lex

            elif magazine.get_top() == neterm_Type:
                magazine.pop()
                if t == TShort:
                    uk1 = sc.get_uk()
                    lex1, t1 = sc.scan()
                    sc.put_uk(uk1)
                    if t1 == TInt:
                        magazine.push(TInt)
                        magazine.push(TShort)
                    del lex1, t1
                elif t == TDouble:
                    magazine.push(TDouble)
                elif t == TIdent:
                    magazine.push(TIdent)
                else:
                    epsilon()

            elif magazine.get_top() == neterm_Main:
                magazine.pop()
                magazine.push(proc_end_main)
                magazine.push(neterm_Block)
                magazine.push(proc_main)
                magazine.push(TRBracket)
                magazine.push(TLBracket)
                magazine.push(TMain)
                magazine.push(TInt)
                magazine.push(TShort)
                current_variable.name = 'блок'
                v0 = tree.semantic_include(current_variable.name, current_variable.type_)

            elif magazine.get_top() == proc_main:
                magazine.pop()
                triads.append(generate_triad(TMain, operand1=Operand('main')))
            elif magazine.get_top() == proc_end_main:
                magazine.pop()
                triads.append(generate_triad(TEnd, operand1=Operand('main')))

            elif magazine.get_top() == neterm_ListOfVariables:
                magazine.pop()
                magazine.push(neterm_AdditionallyList)
                magazine.push(neterm_Variable)
            elif magazine.get_top() == neterm_AdditionallyList:
                if t == TComma:
                    magazine.push(neterm_AdditionallyList)
                    magazine.push(neterm_Variable)
                    magazine.push(TComma)
                else:
                    epsilon()

            elif magazine.get_top() == neterm_Struct:
                magazine.pop()
                magazine.push(TSemicolon)
                magazine.push(TRBrace)
                magazine.push(neterm_DescriptionsStruct)
                magazine.push(TLBrace)
                magazine.push(TIdent)
                magazine.push(TStruct)
                uk = sc.get_uk()
                current_variable.name, t1 = sc.scan()
                del t1
                sc.put_uk(uk)
                v0 = tree.semantic_include(current_variable.name,
                                           current_variable.type_,
                                           current_variable.id_struct)
            elif magazine.get_top() == neterm_DescriptionsStruct:
                if t == TShort:
                    uk1 = sc.get_uk()
                    lex1, t1 = sc.scan()
                    sc.put_uk(uk1)
                    if t1 == TInt:
                        magazine.push(neterm_DescriptionsStruct)
                        magazine.push(TSemicolon)
                        magazine.push(neterm_ListOfVariables)
                        magazine.push(neterm_Type)
                        current_variable.type_ = DATA_TYPE.index('TYPE_SHORT_INT')
                    else:
                        sc.print_error("Ошибка, ожидался", "int")
                    del lex1, t1
                elif (t == TDouble) | (t == TIdent):
                    magazine.push(neterm_DescriptionsStruct)
                    magazine.push(TSemicolon)
                    magazine.push(neterm_ListOfVariables)
                    magazine.push(neterm_Type)
                    if t == TDouble:
                        current_variable.type_ = DATA_TYPE.index('TYPE_DOUBLE')
                    else:
                        current_variable.type_ = DATA_TYPE.index('TYPE_STRUCT')
                        current_variable.id_struct = lex
                else:
                    tree.set_current(v0)
                    epsilon()

            elif magazine.get_top() == neterm_Variable:
                magazine.pop()
                magazine.push(neterm_Initialization)
                magazine.push(TIdent)
                current_variable.name = lex
                tree.semantic_include(current_variable.name,
                                      current_variable.type_,
                                      current_variable.id_struct)
                operands.push(Operand(lex))
            elif magazine.get_top() == neterm_Initialization:
                if t == TAssignment:
                    magazine.pop()
                    magazine.push(proc_initialization)
                    magazine.push(neterm_PriorityLevel1)
                    magazine.push(TAssignment)
                    operations.push(TAssignment)
                else:
                    epsilon()
                    operands.pop()
            elif magazine.get_top() == proc_initialization:
                magazine.pop()
                triads.append(generate_triad(operations.pop(), operands.pop(), operands.pop()))

            elif magazine.get_top() == neterm_Block:
                magazine.pop()
                magazine.push(TRBrace)
                magazine.push(neterm_ContentOfBlock)
                magazine.push(TLBrace)
            elif magazine.get_top() == neterm_DescriptionsInBlock:
                magazine.pop()
                if t == TStruct:
                    magazine.push(neterm_Struct)
                    current_variable.type_ = DATA_TYPE.index('TYPE_STRUCT')
                    current_variable.is_struct = True
                elif t == TShort:
                    uk1 = sc.get_uk()
                    lex1, t1 = sc.scan()
                    sc.put_uk(uk1)
                    if t1 == TInt:
                        magazine.push(TSemicolon)
                        magazine.push(neterm_ListOfVariables)
                        magazine.push(neterm_Type)
                        current_variable.type_ = DATA_TYPE.index('TYPE_SHORT_INT')
                    else:
                        sc.print_error("Ошибка, ожидался", "int")
                    del lex1, t1
                else:
                    magazine.push(TSemicolon)
                    magazine.push(neterm_ListOfVariables)
                    magazine.push(neterm_Type)
                    if t == TDouble:
                        current_variable.type_ = DATA_TYPE.index('TYPE_DOUBLE')
                    else:
                        current_variable.type_ = DATA_TYPE.index('TYPE_STRUCT')
                        current_variable.id_struct = lex
            elif magazine.get_top() == neterm_ContentOfBlock:
                uk = sc.get_uk()
                lex1, t1 = sc.scan()
                sc.put_uk(uk)
                if ((t1 == TIdent) or (t == TShort)) and (t != TLBrace):
                    magazine.push(neterm_ContentOfBlock)
                    magazine.push(neterm_DescriptionsInBlock)
                elif (t == TLBrace) or (t1 != TIdent) and (t != TRBrace):
                    magazine.push(neterm_ContentOfBlock)
                    magazine.push(neterm_Operator)
                else:
                    epsilon()
                current_variable.id_struct = None
                del lex1, t1

            elif magazine.get_top() == neterm_Operator:
                magazine.pop()
                if t == TLBrace:
                    magazine.push(neterm_CompositeOperator)
                elif t == TSemicolon:
                    magazine.push(TSemicolon)
                elif t == TIf:
                    magazine.push(neterm_If)
                elif t == TIdent:
                    magazine.push(neterm_Assignment)
                else:
                    epsilon()

            elif magazine.get_top() == neterm_CompositeOperator:
                magazine.pop()
                magazine.push(neterm_Block)
                current_variable.name = 'блок'
                v0 = tree.semantic_include(current_variable.name, 0)

            elif magazine.get_top() == neterm_Assignment:
                magazine.pop()
                magazine.push(TSemicolon)
                magazine.push(proc_assignement)
                magazine.push(neterm_PriorityLevel1)
                magazine.push(TAssignment)
                magazine.push(neterm_VariableOrElementOfStruct)
                operations.push(TAssignment)
            elif magazine.get_top() == proc_assignement:
                magazine.pop()
                triads.append(generate_triad(operations.pop(), operands.pop(), operands.pop()))

            elif magazine.get_top() == neterm_VariableOrElementOfStruct:
                magazine.pop()
                magazine.push(neterm_ElementOfStruct)
                magazine.push(TIdent)
                operands.push(Operand(lex))
            elif magazine.get_top() == neterm_ElementOfStruct:
                if t == TDotLink:
                    magazine.push(neterm_ElementOfStruct)
                    magazine.push(TIdent)
                    magazine.push(TDotLink)
                else:
                    epsilon()

            elif magazine.get_top() == neterm_If:
                magazine.pop()
                magazine.push(neterm_Else)
                magazine.push(proc_goto)
                magazine.push(neterm_Operator)
                magazine.push(proc_if)
                magazine.push(TRBracket)
                magazine.push(neterm_PriorityLevel1)
                magazine.push(TLBracket)
                magazine.push(TIf)
            elif magazine.get_top() == neterm_Else:
                magazine.pop()
                if t == TElse:
                    magazine.push(proc_exit_from_if)
                    magazine.push(neterm_Operator)
                    magazine.push(TElse)
                else:
                    epsilon()
                    magazine.push(proc_exit_from_if)
            elif magazine.get_top() == proc_if:
                magazine.pop()
                if len(operands) > 0:
                    triads.append(generate_triad(TCmp,
                                                 operand1=operands.pop(),
                                                 operand2=Operand(0)))
                stack_for_ifs.push(len(triads))
                triads.append(generate_triad(TIf,
                                             operand1=Operand(len(triads) + 1, is_address=True),
                                             operand2=Operand('_')))
            elif magazine.get_top() == proc_goto:
                magazine.pop()
                triads[stack_for_ifs.pop()].value[2] = Operand(len(triads) + 1, is_address=True)
                address_goto = len(triads)
                stack_for_ifs.push(address_goto)
                del address_goto
                triads.append(generate_triad(TGoto, operand1=Operand('_')))
            elif magazine.get_top() == proc_exit_from_if:
                magazine.pop()
                triads[stack_for_ifs.pop()].value[1] = Operand(len(triads), is_address=True)
                triads.append(generate_triad(TNope))

            elif magazine.get_top() == proc_generate_triad_for_operation:
                magazine.pop()
                triads.append(generate_triad(operations.pop(), operands.pop(), operands.pop()))
                operands.push(Operand(len(triads) - 1, is_address=True))

            elif magazine.get_top() == neterm_PriorityLevel1:
                magazine.pop()
                magazine.push(neterm_PL1)
                magazine.push(neterm_PriorityLevel2)
            elif magazine.get_top() == neterm_PL1:
                if t == TMore:
                    magazine.push(neterm_PL1)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_PriorityLevel2)
                    magazine.push(TMore)
                    operations.push(TMore)
                elif t == TLess:
                    magazine.push(neterm_PL1)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_PriorityLevel2)
                    magazine.push(TLess)
                    operations.push(TLess)
                elif t == TMoreEqual:
                    magazine.push(neterm_PL1)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_PriorityLevel2)
                    magazine.push(TMoreEqual)
                    operations.push(TMoreEqual)
                elif t == TLessEqual:
                    magazine.push(neterm_PL1)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_PriorityLevel2)
                    magazine.push(TLessEqual)
                    operations.push(TLessEqual)
                else:
                    epsilon()

            elif magazine.get_top() == neterm_PriorityLevel2:
                magazine.pop()
                magazine.push(neterm_PL2)
                magazine.push(neterm_PriorityLevel3)
            elif magazine.get_top() == neterm_PL2:
                if t == TRShift:
                    magazine.push(neterm_PL2)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_PriorityLevel3)
                    magazine.push(TRShift)
                    operations.push(TRShift)
                elif t == TLShift:
                    magazine.push(neterm_PL2)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_PriorityLevel3)
                    magazine.push(TLShift)
                    operations.push(TLShift)
                else:
                    epsilon()

            elif magazine.get_top() == neterm_PriorityLevel3:
                magazine.pop()
                magazine.push(neterm_PL3)
                magazine.push(neterm_PriotityLevel4)
            elif magazine.get_top() == neterm_PL3:
                if t == TPlus:
                    magazine.push(neterm_PL3)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_PriotityLevel4)
                    magazine.push(TPlus)
                    operations.push(TPlus)
                elif t == TMinus:
                    magazine.push(neterm_PL3)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_PriotityLevel4)
                    magazine.push(TMinus)
                    operations.push(TMinus)
                else:
                    epsilon()

            elif magazine.get_top() == neterm_PriotityLevel4:
                magazine.pop()
                magazine.push(neterm_PL4)
                magazine.push(neterm_ElementaryExpression)
            elif magazine.get_top() == neterm_PL4:
                if t == TMul:
                    magazine.push(neterm_PL4)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_ElementaryExpression)
                    magazine.push(TMul)
                    operations.push(TMul)
                elif t == TMod:
                    magazine.push(neterm_PL4)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_ElementaryExpression)
                    magazine.push(TMod)
                    operations.push(TMod)
                elif t == TDiv:
                    magazine.push(neterm_PL4)
                    magazine.push(proc_generate_triad_for_operation)
                    magazine.push(neterm_ElementaryExpression)
                    magazine.push(TDiv)
                    operations.push(TDiv)
                else:
                    epsilon()

            elif magazine.get_top() == neterm_ElementaryExpression:
                magazine.pop()
                if t == TIdent:
                    magazine.push(neterm_VariableOrElementOfStruct)
                elif t == TLBracket:
                    magazine.push(TRBracket)
                    magazine.push(neterm_PriorityLevel1)
                    magazine.push(TLBracket)
                else:
                    magazine.push(neterm_Const)

            elif magazine.get_top() == neterm_Const:
                magazine.pop()
                if (t == TConstInt10) | (t == TConstDoubleExp):
                    magazine.push(t)
                    if t == TConstInt10:
                        operands.push(Operand(int(lex)))
                    else:
                        operands.push(Operand(float(lex)))
            else:
                sc.print_error("Неверный символ", lex)

    # tree.print()
    return triads, tree


def print_triads(triads):
    znak = ''
    i = 0
    for triad in triads:
        if triad.value[0] == TAssignment:
            znak = '='
        elif triad.value[0] == TPlus:
            znak = '+'
        elif triad.value[0] == TMinus:
            znak = '-'
        elif triad.value[0] == TDiv:
            znak = '/'
        elif triad.value[0] == TMod:
            znak = '%'
        elif triad.value[0] == TMul:
            znak = '*'
        elif triad.value[0] == TRShift:
            znak = '>>'
        elif triad.value[0] == TLShift:
            znak = '<<'
        elif triad.value[0] == TMore:
            znak = '>'
        elif triad.value[0] == TLess:
            znak = '<'
        elif triad.value[0] == TMoreEqual:
            znak = '>='
        elif triad.value[0] == TLessEqual:
            znak = '<='
        elif triad.value[0] == TMain:
            znak = 'proc'
        elif triad.value[0] == TEnd:
            znak = 'endproc'
        elif triad.value[0] == TIf:
            znak = 'if'
        elif triad.value[0] == TGoto:
            znak = 'goto'
        elif triad.value[0] == TNope:
            znak = 'nope'
        elif triad.value[0] == TCmp:
            znak = 'cmp'
        if triad.value[1] is None:
            print(str(triad.number) + ')', znak)
        elif triad.value[2] is None:
            print(str(triad.number) + ')',
                  znak,
                  triad.value[1].value if not triad.value[1].is_address else '(' + str(triad.value[1].value) + ')')
        else:
            print(str(triad.number) + ')',
                  znak,
                  triad.value[1].value if not triad.value[1].is_address else '(' + str(triad.value[1].value) + ')',
                  triad.value[2].value if not triad.value[2].is_address else '(' + str(triad.value[2].value) + ')')


def optimization_if(triads):
    number_if = 0
    for triad in triads:
        if triad.value[0] == TIf:
            number_if += 1
    while number_if > 0:
        begin_triads = []
        level = 0
        begin_if = 0
        begin_else = 0
        shift = 0
        for i in range(len(triads)):
            if triads[i].value[0] == TIf and not triads[i].is_optimised:
                if level == 0:
                    begin_if = i + 1
                level += 1
            if triads[i].value[0] == TGoto:
                if level > 0:
                    level -= 1
                    if level == 0:
                        begin_else = i + 1
                        break
                else:
                    continue
        while cmp_triad(triads, triads[begin_if + shift].value,
                        triads[begin_else + shift].value):
            begin_triads.append(triads[begin_if + shift])
            shift += 1
        triads[begin_if - 1].is_optimised = True
        if shift != 0:
            # Обновим адреса перходов для оптимизируемого if-a
            triads[begin_if - 1].value[1].value = triads[begin_if + shift].number
            triads[begin_if - 1].value[2].value = triads[begin_else + shift].number
            # Удаляем совпадающие строки
            for i in range(shift):
                triads.pop(begin_else)
                triads.pop(begin_if)
                begin_else -= 1

            # Создаём триаду для запоминания результата сравнения
            triads.insert(begin_if - 1, generate_triad(TAssignment,
                                                       operand2=Operand(begin_if - 2, is_address=True),
                                                       operand1=Operand('TMP' + str(begin_if - 1))))
            # Записываем совпадаюшие строки после запоминания результата
            for i in range(shift):
                triads.insert(begin_if + i, begin_triads[i].value, begin_triads[i].number)
            # Восстанавливаем значение результата сравнения в регистре
            triads.insert(begin_if + shift, generate_triad(TCmp,
                                                           operand1=triads[begin_if - 1].value[1],
                                                           operand2=Operand(0)))
        # print('------------------------')
        # print_triads(triads)
        end_if = triads.index(triads.get_item(triads[begin_if + shift + 1].value[2].value)) - 2
        end_else = triads.index(triads.get_item(triads[end_if + 1].value[1].value)) - 1
        while True:
            if triads[end_if].value[0] == TAssignment and \
                            triads[end_else].value[0] == TAssignment:
                if cmp_triad(triads, triads[end_if].value, triads[end_else].value):
                    triads_of_assignement = get_assignement(triads, [], triads[end_if].number)
                    triads_of_assignement.sort(key=lambda triad1: triad1.number)
                    triads = delete_assignement(triads, triads[end_else].number)
                    triads = delete_assignement(triads, triads[end_if].number)
                    end_if -= len(triads_of_assignement)
                    end_else -= 2 * len(triads_of_assignement)
                    # print('------------------------')
                    # print_triads(triads)
                    for i in range(len(triads_of_assignement)):
                        triads.insert(end_else + 2 + i, triads_of_assignement[i].value, triads_of_assignement[i].number)
                else:
                    break
            else:
                break

        number_if = 0
        for triad in triads:
            if triad.value[0] == TIf and not triad.is_optimised:
                number_if += 1
    return triads

def delete_assignement(triads: List, number):
    if triads.get_item(number).value[1].is_address:
        triads = delete_assignement(triads, triads.get_item(triads.get_item(number).value[1].value).number)
    if triads.get_item(number).value[2].is_address:
        triads = delete_assignement(triads, triads.get_item(triads.get_item(number).value[2].value).number)
    triads.pop(triads.index(triads.get_item(number)))
    return triads


def get_assignement(triads, triads_of_assignement, number):
    triads_of_assignement.append(triads.get_item(number))
    if triads.get_item(number).value[1].is_address:
        triads_of_assignement = get_assignement(triads, triads_of_assignement,
                                                    triads.get_item(triads.get_item(number).value[1].value).number)
    if triads.get_item(number).value[2].is_address:
        triads_of_assignement = get_assignement(triads, triads_of_assignement,
                                                    triads.get_item(triads.get_item(number).value[2].value).number)
    return triads_of_assignement


def cmp_triad(triads, triad1, triad2):
    if triad1[0] != triad2[0]:
        return False
    elif triad1[0] == TNope:
        return True
    elif triad1[0] == TGoto:
        if triad1[1].is_address and not cmp_triad(triads, triads.get_item(triad1[1].value).value,
                                                  triads.get_item(triad2[1].value).value):
            return False
    elif not triad1[1].is_address and \
            not triad1[2].is_address and \
            not triad2[1].is_address and \
            not triad2[2].is_address:
        if triad1[1] != triad2[1] or triad1[2] != triad2[2]:
            return False
    else:
        if triad1[1].is_address and not triad2[1].is_address or \
                        triad1[2].is_address and not triad2[2].is_address or \
                        triad2[1].is_address and not triad1[1].is_address or \
                        triad2[2].is_address and not triad1[2].is_address:
            return False
        else:
            if triad1[1].is_address and not cmp_triad(triads, triads.get_item(triad1[1].value).value,
                                                      triads.get_item(triad2[1].value).value):
                return False
            elif not triad1[1].is_address and triad1[1].value != triad2[1].value:
                return False
            if triad1[2].is_address and not cmp_triad(triads, triads.get_item(triad1[2].value).value,
                                                      triads.get_item(triad2[2].value).value):
                return False
            elif not triad1[2].is_address and triad1[2].value != triad2[2].value:
                return False
    return True


def generate_triad(operation, operand2=None, operand1=None):
    return [operation, operand1, operand2]


def __main__():
    sc = TScanner('test.txt')
    triads, tree = ll1(sc)
    # print_triads(triads)
    print_triads(optimization_if(triads))
    print('Синтаксических ошибок не обнаружено!')


if __name__ == '__main__':
    __main__()
