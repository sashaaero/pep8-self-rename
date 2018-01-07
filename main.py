# -*- encoding: utf8 -*-

import re
import glob
import sys

classname_pat = r'class ([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]'
method_pat = r'def ([a-zA-Z_][a-zA-Z0-9_-]*)\s*\(([a-zA-Z_][a-zA-Z0-9_-]*)[,|)]'
arg_pat = lambda x: r'(?<!\.)\b(%s)(\.)?' % x


def extract_class(line, indent):
    match = re.search(classname_pat, line)
    if not match:
        raise SyntaxError(line)
    class_name = match.group(1)
    return {'$class_name': class_name, '$indent': indent}


def extract_method(line, indent, classmethod_=None):
    match = re.search(method_pat, line)
    if not match:
        print(method_pat)
        print(line)
        raise SyntaxError(line)
    method_name, first_arg = match.groups()
    first_arg = 'self' if not classmethod_ else 'cls'
    print("In %s rename first arg to %s" % (method_name, first_arg))
    return {'$method_name': method_name, '$first_arg': first_arg, '$indent': indent}


def run2(file):
    curr_class, curr_method, curr_decorator = (None,) * 3 # oh my god I am genius

    lines = file.readlines()
    for line_ in lines:
        line = line_.lstrip()
        indent = len(line_) - len(line)
        if (line_.strip()) == '':
            continue

        if not curr_class:
            if line.startswith('class'):
                curr_class = extract_class(line, indent)
                print(curr_class)
                continue
        else:  # curr_class is not None
            if indent <= curr_class['$indent']:
                if line.startswith('class'):
                    curr_class = extract_class(line, indent)
                    print(curr_class)
                    continue
                else:
                    curr_class = None
                    continue

            if not curr_method:
                if line.startswith('def'):
                    if curr_decorator is not staticmethod:
                        curr_method = extract_method(line, indent, curr_decorator is classmethod)
                        curr_decorator = None  # we don't need it anymore
                elif line.startswith('@classmethod'):
                    curr_decorator = classmethod
                elif line.startswith('@staticmethod'):
                    curr_decorator = staticmethod

            else:  # curr_method is not None
                if indent < curr_method['$indent']:
                    curr_method = None
                    curr_class = extract_class(line, indent) if line.startswith('class') else None
                elif indent == curr_method['$indent']: # that means we found another method or decorator
                    curr_method = None
                    if line.startswith('def'):
                        if curr_decorator is not staticmethod:
                            curr_method = extract_method(line, indent, curr_decorator is classmethod)
                            curr_decorator = None
                    elif line.startswith('@staticmethod'):
                        curr_decorator = staticmethod
                    elif line.startswith('@classmethod'):
                        curr_decorator = classmethod
                    else:
                        curr_method = None
                else: # seems we are in a method scope
                    pass # not implemented


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Incorrect input')
        sys.exit(1)

    filemask = sys.argv[1]
    files = glob.glob(filemask)
    if len(files) != 1:
        print('Multiple or no files were found by "%s"' % filemask)
        sys.exit(1)
    print(files)
    file = open(files[0], 'r')
    run2(file)
