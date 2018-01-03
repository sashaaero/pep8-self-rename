# -*- encoding: utf8 -*-

import re
import glob
import sys

classname_pat = r'class ([a-zA-Z_][a-zA-Z0-9_]*)[\(:]'
method_pat = r'def ([a-zA-Z0-9_][a-zA-Z0-9_]*)\(([a-zA-Z0-9_][a-zA-Z0-9_]*)[\),]'
arg_pat = lambda x: r'(?<!\.)\b(%s)(\.)?' % x

def exctract_class(line, indent):
    match = re.search(classname_pat, line)
    if not match:
        raise SyntaxError(line)
    class_name = match.group(1)
    return {'$class_name': class_name, '$indent': indent}


def run2(file):
    curr_class, curr_method, curr_decorator = (None,) * 3 # oh my god I am genius

    lines = file.readlines()
    for line_ in lines:
        line = line_.lstrip()
        indent = len(line_) - len(line)

        if not curr_class:
            if line.startswith('class'):
                curr_class = exctract_class(line, indent)
                print(curr_class)
                continue
        else:  # curr_class is not None
            if indent <= curr_class['$indent']:
                if line.startswith('class'):
                    curr_class = exctract_class(line, indent)
                    print(curr_class)
                    continue
                else:
                    curr_class = None
                    continue

def run(file):
    lines = list(file.readlines())
    out = open('%s_out.py' % file.name[:-3], 'w')



    curr_class = {}
    decorator = None
    curr_method = {}

    i = 0

    while i < len(lines):
        line_ = lines[i]
        out.write(line_)

        if len(line_.strip()) == 0:
            i += 1
            continue

        line = line_.lstrip()

        if line.startswith('#') or line.startswith('"') or line.startswith("'"):
            i += 1
            continue

        indent = len(line_) - len(line)

        if curr_class:
            if indent <= curr_class['$indent']:
                curr_class.clear()
                i += 1
                continue

            if not curr_method:

                if line.startswith('@classmethod'):
                    decorator = classmethod
                    i += 1
                    continue

                if line.startswith('@staticmethod'):
                    decorator = staticmethod
                    i += 1
                    continue

                # we don`t care about other decorators

                if line.startswith('def'):
                    if decorator == staticmethod:
                        decorator = None
                        i += 1
                        continue

                    match = re.search(method_pat, line)
                    if not match:
                        print(line)
                        print(decorator)
                        raise SyntaxError('Line %d of %s seems incorrect' % (i+1, file.name))
                    method_name, first_arg = match.groups()

                    curr_method = {'$method_name': method_name, '$indent': indent}

                    curr_method['$rename'] = 'self' if decorator != classmethod else 'cls'
                    curr_method['$first_arg'] = first_arg

                    print('In %s.%s rename %s to %s' %
                          (curr_class['$class_name'], curr_method['$method_name'], curr_method['$first_arg'],
                           curr_method['$rename']))

                    i += 1
                    continue
            else:
                # assuming that we are in method scope now
                if indent <= curr_method['$indent']:
                    curr_method.clear()
                    decorator = None
                    continue

                else:
                    pat = arg_pat(curr_method['$first_arg'])
                    res = re.match(pat, line)
                    print(res)
                    i += 1
                    continue

        if not curr_class:
            # check for class
            if line.startswith('class'):
                # extract class name
                classname = re.search(classname_pat, line).group(1)
                curr_class['$class_name'] = classname
                curr_class['$indent'] = indent
        i += 1

    out.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Incorrect input')
        sys.exit(1)

    filemask = sys.argv[1]
    files = glob.glob(filemask)
    if len(files) != 1:
        print('Multiple or no files were found by "%s"' % filemask)
        sys.exit(1)

    file = open(files[0], 'r')
    run2(file)
