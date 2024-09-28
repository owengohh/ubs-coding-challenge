import json
import logging
import re
from flask import request

from routes import app

logger = logging.getLogger(__name__)

variables = {}

class InterpreterError(Exception):
    def __init__(self, message):
        super().__init__(message)

def tokenise(expression):
    # regex pattern to match parentheses, strings, and other tokens
    token_pattern = r'''\s*(?:(\()|(\))|("(?:\\.|[^"\\])*")|([^\s()]+))'''
    tokens = []
    for match in re.findall(token_pattern, expression):
        if match[0]:  # Left parenthesis
            tokens.append('(')
        elif match[1]:  # Right parenthesis
            tokens.append(')')
        elif match[2]:  # String literal
            tokens.append(match[2])
        elif match[3]:  # Atom
            tokens.append(match[3])
    logging.info("tokens" + str(tokens))
    return tokens

def parse(tokens):
    # handles brackets
    if len(tokens) == 0:
        raise InterpreterError('Unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        stack = []
        while tokens[0] != ')':
            stack.append(parse(tokens))
            if len(tokens) == 0:
                raise InterpreterError('Unexpected EOF')
        tokens.pop(0)  # remove the closing brace
        return stack
    elif token == ')':
        raise InterpreterError('Unexpected )')
    else:
        return convert(token)

def convert(token):
    # process tokens after tokenising to what is understood in python code
    # String literals (including quotes)
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    elif token == 'true':
        return True
    elif token == 'false':
        return False
    elif token == 'null':
        return None
    else:
        try:
            if '.' in token:
                return float(token)
            else:
                return int(token)
        except ValueError:
            return token  # Variable name or function name


def evaluate_expression(expression, line_number, variables):
    tokens = tokenise(expression)
    tokensToEval = parse(tokens)
    result = evaluate(tokensToEval, line_number, variables)
    if result is None:
        return None
    elif isinstance(result, bool):
        return 'true' if result else 'false'
    else:
        return str(result)

def evaluate(toEval, line_number, variables):
    logging.info("hit eval")
    if isinstance(toEval, str):
        if toEval in variables:
            return variables[toEval]
        else:
            return toEval
    elif not isinstance(toEval, list) or len(toEval) == 0:
        # numbers, booleans, None
        return toEval
    else:
        # requires our function call
        if len(toEval) == 0:
            raise InterpreterError(f'ERROR at line {line_number}')
        funcName = toEval[0]
        args = toEval[1:]
        # note that args can be an empty list so we need to account for that
        if not isinstance(funcName, str):
            raise InterpreterError(f'ERROR at line {line_number}')
        return functions(funcName, args, line_number, variables)


def functions(func_name, args, line_number, variables):
    if func_name in function_table:
        return function_table[func_name](args, line_number, variables)
    else:
        raise InterpreterError(f'ERROR at line {line_number}')

def mySet(args, line_number, variables):
    logging.info("hit set")
    if len(args) != 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    var_name = args[0]
    if not isinstance(var_name, str) or not var_name.isidentifier():
        raise InterpreterError(f'ERROR at line {line_number}')
    if var_name in variables:
        raise InterpreterError(f'ERROR at line {line_number}')
    value = evaluate(args[1], line_number, variables)
    variables[var_name] = value
    return None

def myPuts(args, line_number, variables):
    logging.info("hit puts")
    if len(args) != 1:
        raise InterpreterError(f'ERROR at line {line_number}')
    value = evaluate(args[0], line_number, variables)
    if not isinstance(value, str):
        raise InterpreterError(f'ERROR at line {line_number}')
    return value

def format_number(value):
    if isinstance(value, float):
        value = round(value + 1e-8, 4)
        value_str = f"{value:.4f}".rstrip('0').rstrip('.')
        return float(value_str) if '.' in value_str else int(value_str)
    return value

def add(args, line_number, variables):
    logging.info("hit add")
    if len(args) < 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    total = 0
    for arg in args:
        value = evaluate(arg, line_number, variables)
        if not isinstance(value, (int, float)):
            raise InterpreterError(f'ERROR at line {line_number}')
        total += value
    return format_number(total)

def concat(args, line_number, variables):
    logging.info("hit concat")
    if len(args) != 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    str1 = evaluate(args[0], line_number, variables)
    str2 = evaluate(args[1], line_number, variables)
    if not isinstance(str1, str) or not isinstance(str2, str):
        raise InterpreterError(f'ERROR at line {line_number}')
    return str1 + str2

def lowercase(args, line_number, variables):
    logging.info("hit lowercase")
    if len(args) != 1:
        raise InterpreterError(f'ERROR at line {line_number}')
    s = evaluate(args[0], line_number, variables)
    if not isinstance(s, str):
        raise InterpreterError(f'ERROR at line {line_number}')
    return s.lower()

def uppercase(args, line_number, variables):
    logging.info("hit uppercase")
    if len(args) != 1:
        raise InterpreterError(f'ERROR at line {line_number}')
    s = evaluate(args[0], line_number, variables)
    if not isinstance(s, str):
        raise InterpreterError(f'ERROR at line {line_number}')
    return s.upper()

def replace(args, line_number, variables):
    logging.info("hit replace")
    if len(args) != 3:
        raise InterpreterError(f'ERROR at line {line_number}')
    source = evaluate(args[0], line_number, variables)
    target = evaluate(args[1], line_number, variables)
    replacement = evaluate(args[2], line_number, variables)
    if not all(isinstance(s, str) for s in [source, target, replacement]):
        raise InterpreterError(f'ERROR at line {line_number}')
    return source.replace(target, replacement)

def substring(args, line_number, variables):
    logging.info("hit substring")
    if len(args) != 3:
        raise InterpreterError(f'ERROR at line {line_number}')
    source = evaluate(args[0], line_number, variables)
    start = evaluate(args[1], line_number, variables)
    end = evaluate(args[2], line_number, variables)
    if not isinstance(source, str):
        raise InterpreterError(f'ERROR at line {line_number}')
    if not all(isinstance(i, (int, float)) for i in [start, end]):
        raise InterpreterError(f'ERROR at line {line_number}')
    start = int(start)
    end = int(end)
    if start < 0 or end < 0 or start > len(source) or end > len(source) or start > end:
        raise InterpreterError(f'ERROR at line {line_number}')
    return source[start:end]

def subtract(args, line_number, variables):
    logging.info("hit subtract")
    if len(args) != 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    num1 = evaluate(args[0], line_number, variables)
    num2 = evaluate(args[1], line_number, variables)
    if not all(isinstance(n, (int, float)) for n in [num1, num2]):
        raise InterpreterError(f'ERROR at line {line_number}')
    result = num1 - num2
    return format_number(result)

def multiply(args, line_number, variables):
    logging.info("hit multiply")
    if len(args) < 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    total = 1
    for arg in args:
        value = evaluate(arg, line_number, variables)
        if not isinstance(value, (int, float)):
            raise InterpreterError(f'ERROR at line {line_number}')
        total *= value
    return format_number(total)

def divide(args, line_number, variables):
    logging.info("hit divide")
    if len(args) != 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    dividend = evaluate(args[0], line_number, variables)
    divisor = evaluate(args[1], line_number, variables)
    if not all(isinstance(n, (int, float)) for n in [dividend, divisor]):
        raise InterpreterError(f'ERROR at line {line_number}')
    if divisor == 0:
        raise InterpreterError(f'ERROR at line {line_number}')
    if isinstance(dividend, int) and isinstance(divisor, int):
        result = dividend // divisor
    else:
        result = dividend / divisor
    return format_number(result)

def myAbs(args, line_number, variables):
    logging.info("hit abs")
    if len(args) != 1:
        raise InterpreterError(f'ERROR at line {line_number}')
    num = evaluate(args[0], line_number, variables)
    if not isinstance(num, (int, float)):
        raise InterpreterError(f'ERROR at line {line_number}')
    result = abs(num)
    return format_number(result)

def myMax(args, line_number, variables):
    logging.info("hit max")
    if len(args) < 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    values = []
    for arg in args:
        value = evaluate(arg, line_number, variables)
        if not isinstance(value, (int, float)):
            raise InterpreterError(f'ERROR at line {line_number}')
        values.append(value)
    result = max(values)
    return format_number(result)

def myMin(args, line_number, variables):
    logging.info("hit min")
    if len(args) < 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    values = []
    for arg in args:
        value = evaluate(arg, line_number, variables)
        if not isinstance(value, (int, float)):
            raise InterpreterError(f'ERROR at line {line_number}')
        values.append(value)
    result = min(values)
    return format_number(result)

def gt(args, line_number, variables):
    logging.info("hit gt")
    if len(args) != 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    num1 = evaluate(args[0], line_number, variables)
    num2 = evaluate(args[1], line_number, variables)
    if not all(isinstance(n, (int, float)) for n in [num1, num2]):
        raise InterpreterError(f'ERROR at line {line_number}')
    return num1 > num2

def lt(args, line_number, variables):
    logging.info("hit lt")
    if len(args) != 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    num1 = evaluate(args[0], line_number, variables)
    num2 = evaluate(args[1], line_number, variables)
    if not all(isinstance(n, (int, float)) for n in [num1, num2]):
        raise InterpreterError(f'ERROR at line {line_number}')
    return num1 < num2

def equal(args, line_number, variables):
    logging.info("hit equal")
    if len(args) != 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    val1 = evaluate(args[0], line_number, variables)
    val2 = evaluate(args[1], line_number, variables)
    allowed_types = (int, float, str, bool, type(None))
    if not isinstance(val1, allowed_types) or not isinstance(val2, allowed_types):
        raise InterpreterError(f'ERROR at line {line_number}')
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        return val1 == val2
    else:
        return type(val1) == type(val2) and val1 == val2

def notEqual(args, line_number, variables):
    logging.info("hit not_equal")
    if len(args) != 2:
        raise InterpreterError(f'ERROR at line {line_number}')
    val1 = evaluate(args[0], line_number, variables)
    val2 = evaluate(args[1], line_number, variables)
    allowed_types = (int, float, str, bool, type(None))
    if not isinstance(val1, allowed_types) or not isinstance(val2, allowed_types):
        raise InterpreterError(f'ERROR at line {line_number}')
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        return val1 != val2
    else:
        return type(val1) != type(val2) or val1 != val2

def myStr(args, line_number, variables):
    logging.info("hit str")
    if len(args) != 1:
        raise InterpreterError(f'ERROR at line {line_number}')
    val = evaluate(args[0], line_number, variables)
    allowed_types = (int, float, str, bool, type(None))
    if not isinstance(val, allowed_types):
        raise InterpreterError(f'ERROR at line {line_number}')
    if val is None:
        return 'null'
    elif isinstance(val, bool):
        if val:
            return 'true'  
        else:
            return 'false'
    else:
        return str(val)

function_table = {
    "set": mySet,
    "puts": myPuts,
    "concat": concat,
    "add": add,
    "lowercase": lowercase,
    "uppercase": uppercase,
    "replace": replace,
    "substring": substring,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "abs": myAbs,
    "max": myMax,
    "min": myMin,
    "gt": gt,
    "lt": lt,
    "equal": equal,
    "not_equal": notEqual,
    "str": myStr
}

@app.route('/lisp-parser', methods=['POST'])
def evaluateMiniInterpreter():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    expressions = data.get("expressions")
    result = {"output": []}
    variables = {}  # Initialize variables per request

    try:
        for i, expression in enumerate(expressions):
            line_number = i + 1
            evaled = evaluate_expression(expression, line_number, variables)
            if evaled is not None:
                result["output"].append(evaled)
    except InterpreterError as e:
        result["output"].append(str(e))
    except Exception as e:
        logging.info("Unexpected Exception : " + str(e))
        result["output"].append(f'ERROR at line {line_number}')
    logging.info("My result :{}".format(result))
    return json.dumps(result)
