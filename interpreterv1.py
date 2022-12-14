from intbase import *
import util
from collections import defaultdict, deque
import controls

class Interpreter(InterpreterBase):

    def __init__(self, console_output=True, input=None, trace_output=False):
        super().__init__(console_output, input)   # call InterpreterBase’s constructor
        self.func_locs = dict()
        self.variables = dict()
        self.call_stack = deque()

        # self.variables['result'] = None

    def run(self, program):
        self.tokenized_lines = [util.tokenize(line) for line in program]
        self.leading_spaces = [len(line) - len(line.lstrip()) for line in program]
        self.find_funcs()
        self.WHILE_controls = defaultdict(controls.Control_WHILE)
        self.ENDWHILE_controls = defaultdict(controls.Control_ENDWHILE)
        self.IF_controls = defaultdict(controls.Control_IF)
        self.ELSE_Controls = defaultdict(controls.Control_ELSE)
        self.setup_controls()

        self.ip = self.func_locs['main'] + 1
        self.call_stack.append(self.ip)

        while len(self.call_stack) > 0:
            self.interpret()
            self.ip += 1

    def interpret(self):
        '''
        Interprets the line that the instruction pointer is on.
        '''
        stack = []
        for token in reversed(self.tokenized_lines[self.ip]):
            match token:
                case self.ASSIGN_DEF:
                    self.interpret_ASSIGN(stack)
                case self.FUNCCALL_DEF:
                    self.interpret_FUNCCALL(stack)
                case self.ENDFUNC_DEF:
                    # TODO: throw error if stack is not empty
                    self.ip = self.call_stack.pop()
                case self.RETURN_DEF:
                    self.interpret_RETURN(stack)
                case '+' | '-' | '*' | '/' | '%' | '<' | '<=' | '>' | '>=' | '!=' | '==' | '&' | '|':
                    self.interpret_EXPRESSION(token, stack)
                case self.WHILE_DEF:
                    self.interpret_WHILE(stack)
                case self.ENDWHILE_DEF:
                    self.interpret_ENDWHILE()
                case self.IF_DEF:
                    self.interpret_IF(stack)
                case self.ELSE_DEF:
                    self.interpret_ELSE()
                case _:
                    stack.append(token)
        # print(self.tokenized_lines[self.ip])

    def interpret_WHILE(self, stack):
        condition = stack.pop()
        if condition in self.variables:
            condition = self.variables[condition]
        if not isinstance(condition, bool):
            # TODO: throw an error, while condition must be a bool
            pass
        if condition != True:
            self.ip = self.WHILE_controls[self.ip].ENDWHILE_line

    def interpret_ENDWHILE(self):
        self.ip = self.ENDWHILE_controls[self.ip].WHILE_line - 1

    def interpret_IF(self, stack):
        condition = stack.pop()
        if condition in self.variables:
            condition = self.variables[condition]
        if not isinstance(condition, bool):
            # TODO: throw an error, if condition must be a bool
            pass
        if condition != True:
            else_line = self.IF_controls[self.ip].ELSE_line
            if else_line != None:
                self.ip = else_line
            else:
                self.ip = self.IF_controls[self.ip].ENDIF_line

    def interpret_ELSE(self):
        self.ip = self.ELSE_Controls[self.ip].ENDIF_line

    def interpret_EXPRESSION(self, expression, stack):
        a = stack.pop()
        a1 = a
        if a in self.variables:
            a = self.variables[a]
            a1 = a
        if isinstance(a, str) and a[0] == '"' and a[-1] == '"': # String
            a = a[1:-1]
        elif a == 'True' or a == 'False': # Boolean
            a = a == 'True'
        elif isinstance(a, str) and a.isnumeric(): # Integer
            a = int(a)
        b = stack.pop()
        b1 = b
        if b in self.variables:
            b = self.variables[b]
            b1 = b
        if isinstance(b, str) and b[0] == '"' and b[-1] == '"': # String
            b = b[1:-1]
        elif b == 'True' or b == 'False': # Boolean
            b = b == 'True'
        elif isinstance(b, str) and b.isnumeric(): # Integer
            b = int(b)

        #if isinstance(a, str) and isinstance(b, str) and a[0] == '"' and b[0] == '"' and a[1] == '"' and b[1] == '"':
        #    pass # do nothing bc its a string
        #elif a != 'True' and a != 'False' and b != 'True' and b != 'False':
        #    a, b = int(a), int(b)
        result = None
        if type(a) != type(b):
            super().error(ErrorType.TYPE_ERROR, line_num=self.ip)
        match expression:
            case '+':
                result = a + b
            case '-':
                result = a - b
            case '*':
                result = int(a * b)
            case '/':
                result = int(a / b)
            case '%':
                result = a % b
            case '<':
                result = a < b
            case '<=':
                result = a <= b
            case '>':
                result = a > b
            case '>=':
                result = a >= b
            case '!=':
                result = a != b
            case '==':
                result = a == b
            case '&':
                result = (a == True) and (b == True)
            case '|':
                result = (a1 == 'True') or (b1 == 'True')
        stack.append(result)

    def interpret_ASSIGN(self, stack):
        # TODO: throw error if either value or variable isn't on the stack
        # TODO: get type of variable
        variable = stack.pop()
        value = stack.pop()
        # print(f'value: {value}, variable: {variable}')
        if isinstance(value, str) and value[0] == '"' and value[-1] == '"': # String
            value = value[1:-1]
        elif value == 'True' or value == 'False': # Boolean
            value = value == 'True'
        elif isinstance(value, bool):
            pass
        elif isinstance(value, str) and value.isnumeric() or isinstance(value, int) or isinstance(value, float): # Integer
            value = int(value)
        elif value in self.variables:
            value = self.variables[value]
        #else:
        #    print(value, type(value))
        #    super().error(ErrorType.NAME_ERROR, line_num=self.ip)
        # print(f'value: {value}, variable: {variable}')
        self.variables[variable] = value

    def interpret_FUNCCALL(self, stack):
        func = stack.pop()
        match func:
            case self.PRINT_DEF:
                prompts = self.combine_stack(stack)
                util.output(super(), prompts)
            case self.INPUT_DEF:
                prompts = [e[1:-1] if isinstance(e, str) and e[0] == '"' and e[-1] == '"' else e for e in stack]
                self.variables['result'] = str(util.input(super(), prompts))
            case _:
                # Add the current instruction pointer location and then move to the
                # location of the function definition.
                self.call_stack.append(self.ip)
                # TODO: write a function get_func_loc() to get the location and throw error in
                # case its not a valid function
                self.ip = self.func_locs[func]
    
    def combine_stack(self, stack):
        prompts = []
        while stack:
            i = stack.pop()
            if isinstance(i, str) and len(i) > 1 and i[0] == '"' and i[-1] == '"':
                prompts.append(i[1:-1])
            elif i in self.variables:
                prompts.append(self.variables[i])
            else:
                prompts.append(i)
        return prompts

    def interpret_RETURN(self, stack):
        if len(stack) > 0:
            i = stack.pop()
            if i in self.variables:
                i = self.variables[i]
            self.variables['result'] = i
        else:
            # TODO: throw an error if stack is empty
            pass
        self.ip = self.call_stack.pop()

    def find_funcs(self):
        '''Finds all of the function locations.'''
        for index, tokens in enumerate(self.tokenized_lines):
            if len(tokens) > 0 and tokens[0] == self.FUNC_DEF:
                # TODO: error handling if there is no func name or there are more than 1 tokens after def
                self.func_locs[tokens[1]] = index
    
    def setup_controls(self):
        while_stack = deque()
        if_stack = deque()
        else_stack = deque()

        for index, tokens in enumerate(self.tokenized_lines):
            if not tokens:
                continue
            match tokens[0]:
                case self.WHILE_DEF:
                    while_stack.append(index)
                case self.ENDWHILE_DEF:
                    while_index = while_stack.pop()
                    if self.leading_spaces[while_index] != self.leading_spaces[index]:
                        # TODO: throw a syntax error at line_num=while_index
                        pass
                    self.WHILE_controls[while_index].ENDWHILE_line = index
                    self.ENDWHILE_controls[index].WHILE_line = while_index
                case self.IF_DEF:
                    if_stack.append(index)
                case self.ELSE_DEF:
                    else_stack.append(index)
                    if_index = if_stack[-1] # if_stack.pop()
                    if self.leading_spaces[if_index] != self.leading_spaces[index]:
                        # TODO: throw a syntax error at line_num=if_index
                        pass
                    self.IF_controls[if_index].ELSE_line = index
                case self.ENDIF_DEF:
                    if_index = if_stack.pop()
                    if self.leading_spaces[if_index] != self.leading_spaces[index]:
                        # TODO: throw a syntax error at line_num=if_line
                        pass
                    self.IF_controls[if_index].ENDIF_line = index
                    if len(else_stack) > 0:
                        else_line = else_stack.pop()
                        self.ELSE_Controls[else_line].ENDIF_line = index


    