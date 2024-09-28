import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

variables = {}

def tokenise(expression):
    expression = expression.replace('(', ' ( ')
    expression = expression.replace(')', ' ) ')
    return expression.strip().split()

def parse(tokens):
    if len(tokens) == 0:
        return
    token = tokens.pop(0)
    if token == '(':
        stack = []
        while tokens[0] != ')':
            stack.append(parse(tokens))
            if len(tokens) == 0:
                return
        tokens.pop(0)  # remove the closing brace
        return stack
    elif token == ')':
        logging.info('Unexpected )')
    else:
        return convert(token)

def convert(token):
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    elif token == 'true':
        return True
    elif token == 'false':
        return False
    elif token == 'null':
        return None
    # Number
    else:
        try:
            if '.' in token:
                return float(token)
            else:
                return int(token)
        except ValueError:
            return token


def evaluate_expression(expression):
    tokens = tokenise(expression)
    tokensToEval = parse(tokens)
    result = evaluate(tokensToEval)
    if isinstance(result, list):
        result = [str(val) for val in result]
    elif isinstance(result, bool):
        if result:
            return "true"
        else:
            return "false"
    else:
        return str(result)


def evaluate(toEval):
    if isinstance(toEval, str):
        if toEval in variables:
            return variables[toEval]
        else:
            return toEval
    elif not isinstance(toEval, list) or len(toEval) == 0:
        return toEval
    else:
        funcName = toEval[0]
        args = toEval[1:]
        return functions(funcName, args)

def mySet(args):
    logging.info("hit sets")
    if len(args) != 2:
        return
    var_name = args[0]
    if not isinstance(var_name, str) or not var_name.isidentifier():
        return
    if var_name in variables:
        return
    value = evaluate(args[1])
    variables[var_name] = value

def myPuts(args):
    logging.info("hit puts", args)
    if len(args) != 1:
        return
    value = evaluate(args[0])
    if not isinstance(value, str):
        return
    value = args[0]
    return value

def format_number(value):
    logging.info("hit format_number")
    if isinstance(value, float):
        value = round(value + 1e-8, 4)
        value_str = f"{value:.4f}".rstrip('0').rstrip('.')
        return float(value_str) if '.' in value_str else int(value_str)
    return value

def add(args):
    logging.info("hit add", args)
    if len(args) < 2:
        return
    total = 0
    for arg in args:
        value = evaluate(arg)
        if not isinstance(value, (int, float)):
            return
        total += value
    return format_number(total)


def concat(args):
    logging.info("hit concat", args)
    return "".join(args)

def lowercase(args):
    logging.info("hit lowercase", args)
    return args[0].lower()

def uppercase(args):
    logging.info("hit uppercase", args)
    return args[0].upper()

def replace(args):
    logging.info("hit replace", args)
    if len(args) != 3:
        return
    source = evaluate(args[0])
    target = evaluate(args[1])
    replacement = evaluate(args[2])
    return source.replace(target, replacement)

def substring(args):
    logging.info("hit substring", args)

    if len(args) != 3:
        return
    source = args[0]
    start = args[1]
    end = args[2]
    if not isinstance(source, str):
        return
    if not all(isinstance(i, (int, float)) for i in [start, end]):
        return
    start = int(start)
    end = int(end)
    if start < 0 or end < 0 or start > len(source) or end > len(source) or start > end:
        return
    return source[start:end]

def subtract(args):
    if len(args) != 2:
        return
    num1 = evaluate(args[0])
    num2 = evaluate(args[1])
    if not all(isinstance(n, (int, float)) for n in [num1, num2]):
        return
    result = num1 - num2
    return format_number(result)

def multiply(args):
    if len(args) < 2:
        return
    total = 1
    for arg in args:
        value = evaluate(arg)
        if not isinstance(value, (int, float)):
            return
        total *= value
    return format_number(total)

def divide(args):
    if len(args) != 2:
        return
    dividend = evaluate(args[0])
    divisor = evaluate(args[1])
    if not all(isinstance(n, (int, float)) for n in [dividend, divisor]):
        return
    if divisor == 0:
        return
    if isinstance(dividend, int) and isinstance(divisor, int):
        result = dividend // divisor
    else:
        result = dividend / divisor
    return format_number(result)

def myAbs(args):
    if len(args) != 1:
        return
    num = evaluate(args[0])
    if not isinstance(num, (int, float)):
        return
    result = abs(num)
    return format_number(result)

def myMax(args):
    if len(args) < 2:
        return 
    values = []
    for arg in args:
        value = evaluate(arg)
        if not isinstance(value, (int, float)):
            return
        values.append(value)
    result = max(values)
    return format_number(result)

def myMin(args):
    if len(args) < 2:
        return 
    values = []
    for arg in args:
        value = evaluate(arg)
        if not isinstance(value, (int, float)):
            return 
        values.append(value)
    result = min(values)
    return format_number(result)

def gt(args):
    if len(args) != 2:
        return
    num1 = evaluate(args[0])
    num2 = evaluate(args[1])
    if not all(isinstance(n, (int, float)) for n in [num1, num2]):
        return
    return num1 > num2

def lt(args):
    if len(args) != 2:
        return
    num1 = evaluate(args[0])
    num2 = evaluate(args[1])
    if not all(isinstance(n, (int, float)) for n in [num1, num2]):
        return
    return num1 < num2

def equal(args):
    if len(args) != 2:
        return
    val1 = evaluate(args[0])
    val2 = evaluate(args[1])
    allowed_types = (int, float, str, bool, type(None))
    if not isinstance(val1, allowed_types) or not isinstance(val2, allowed_types):
        return
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        return val1 == val2
    else:
        return type(val1) == type(val2) and val1 == val2

def notEqual(args):
    if len(args) != 2:
        return
    val1 = evaluate(args[0])
    val2 = evaluate(args[1])
    allowed_types = (int, float, str, bool, type(None))
    if not isinstance(val1, allowed_types) or not isinstance(val2, allowed_types):
        return
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        return val1 != val2
    else:
        return type(val1) != type(val2) or val1 != val2

def myStr(args):
    if len(args) != 1:
        return
    val = evaluate(args[0])
    allowed_types = (int, float, str, bool, type(None))
    if not isinstance(val, allowed_types):
        return
    if val is None:
        return 'null'
    elif isinstance(val, bool):
        return 'true' if val else 'false'
    else:
        return str(val)

def dummy():
    return ""

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

def functions(func_name, args):
    if func_name in function_table:
        return function_table[func_name](args)

@app.route('/lisp-parser', methods=['POST'])
def evaluateMiniInterpreter():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    expressions = data.get("expressions")
    result = {"output": []}
    
    for expr in expressions:
        try:
            evaled = evaluate_expression(expr)
            if evaled is not None:
                if isinstance(result, list):
                    result["output"].extend(evaled)
                else:
                    result["output"].append(evaled)
        except Exception as e:
            result["output"].append("ERROR"+ str(e))

    logging.info("My result :{}".format(result))
    return json.dumps(result)
