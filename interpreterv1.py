from intbase import InterpreterBase
import util
from collections import defaultdict, deque

class Interpreter(InterpreterBase):

    def __init__(self, console_output=True, input=None, trace_output=False):
        super().__init__(console_output, input)   # call InterpreterBase’s constructor
        self.func_locs = dict()
        self.variables = dict()
        self.call_stack = deque()

    def run(self, program):
        self.tokenized_lines = [util.tokenize(line) for line in program]
        self.leading_spaces = [len(line) - len(line.lstrip()) for line in program]
        self.find_funcs()

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
                case _:
                    stack.append(token)
        # print(self.tokenized_lines[self.ip])

    def interpret_EXPRESSION(self, expression, stack):
        a = stack.pop()
        a1 = a
        if a in self.variables:
            a = self.variables[a]
            a1 = a
        else:
            if isinstance(a, str) and a[0] == '"' and a[-1] == '"': # String
                pass
            elif isinstance(a, str) and '.' in a: # Floating Point
                a = float(a)
            elif a == 'True' or a == 'False': # Boolean
                a = a == 'True'
            else: # Integer
                a = int(a)
        b = stack.pop()
        b1 = b
        if b in self.variables:
            b = self.variables[b]
            b1 = b
        else:
            if isinstance(b, str) and b[0] == '"' and b[-1] == '"': # String
                pass
            elif isinstance(b, str) and '.' in b: # Floating Point
                b = float(b)
            elif b == 'True' or b == 'False': # Boolean
                b = b == 'True'
            else: # Integer
                b = int(b)

        #if isinstance(a, str) and isinstance(b, str) and a[0] == '"' and b[0] == '"' and a[1] == '"' and b[1] == '"':
        #    pass # do nothing bc its a string
        #elif a != 'True' and a != 'False' and b != 'True' and b != 'False':
        #    a, b = int(a), int(b)
        result = None
        match expression:
            case '+':
                result = a + b
            case '-':
                result = a - b
            case '*':
                result = a * b
            case '/':
                result = a / b
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
        if value[0] == '"' and value[-1] == '"': # String
            pass
        elif '.' in value: # Floating Point
            value = float(value)
        elif value == 'True' or value == 'False': # Boolean
            value = value == 'True'
        else: # Integer
            value = int(value)
        self.variables[variable] = value

    def interpret_FUNCCALL(self, stack):
        func = stack.pop()
        match func:
            case self.PRINT_DEF:
                token = stack.pop()
                if token in self.variables:
                    self.output(self.variables[token])
                else:
                    self.output(token)
            # 
            case _:
                # Add the current instruction pointer location and then move to the
                # location of the function definition.
                self.call_stack.append(self.ip)
                # TODO: write a function get_func_loc() to get the location and throw error in
                # case its not a valid function
                self.ip = self.func_locs[func]
    
    def interpret_RETURN(self, stack):
        if len(stack) > 0:
            self.variables['result'] = stack.pop()
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
    