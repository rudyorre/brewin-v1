from intbase import InterpreterBase
import functools

def tokenize(line):
    '''
    Given a line of a program, strips it of whitespace and tokenizes the string into a list of tokens.
    '''
    line = line.strip()
    tokens = []
    token = ''
    index = 0
    while index < len(line):
        match line[index]:
            case InterpreterBase.COMMENT_DEF:
                # If a comment is run into, everything after should be ignored
                break
            case '"':
                # If a quotation symbol is found, find the next quotation
                # TODO: throw error if next quote cannot be found
                nextQuote = line.index('"', index + 1)
                tokens.append(line[index:nextQuote + 1])
                index = nextQuote + 1
            case ' ':
                # If there is a space and `token` is not empty, we append it
                if token != '':
                    tokens.append(token)
                    token = ''
            case _:
                # Otherwise, add character to current token
                token += line[index]
        index += 1
    if token != '':
        # If there is a remaining token, append it
        tokens.append(token)
    return tokens

def input(interpreter, prompts):
    # prompt = functools.reduce(lambda acc,p: acc+p, prompts, '')
    prompt = ''.join([str(pro) for pro in prompts])
    interpreter.output(prompt)
    return interpreter.get_input()

def output(interpreter, outputs):
    # output = functools.reduce(lambda acc,o: acc+o, outputs, '')
    output = ''.join([str(out) for out in outputs])
    interpreter.output(output)

def is_str(value):
    return value[0] == '"' and value[-1] == '"'

def is_int(value):
    pass
