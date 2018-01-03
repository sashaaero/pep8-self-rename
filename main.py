# -*- encoding: utf8 -*-

import re
import glob
import sys

def run(file):
    lines = list(file.readlines())
    out_lines = []

    classname_pat = r'class ([a-zA-Z_][a-zA-Z0-9_]*)[\(:]'
    method_pat = r'def ([a-zA-Z0-9_][a-zA-Z0-9_]*)\(([a-zA-Z0-9_][a-zA-Z0-9_]*)[\),]'
    arg_pat = lambda x: r'(?<!\.)\b(%s)(\.)?' % x

    curr_class = {}
    decorator = None
    curr_method = {}

    i = 0

    while i < len(lines):
        line_ = lines[i]
        out_lines.append(line_)

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

                # we dont care about other decorators

                if line.startswith('def'):
                    if decorator == staticmethod:
                        decorator = None
                        i += 1
                        continue

                    match = re.search(method_pat, line)
                    if not match:
                        raise SyntaxError('Line %d of %s seems incorrect' % (i+1, file.name))
                    method_name, first_arg = match.groups()

                    curr_method = {'$method_name': method_name, '$indent': indent}

                    curr_method['$rename'] = 'self' if decorator != classmethod else 'cls'
                    curr_method['$first_arg'] = first_arg

                    print('In %s.%s rename %s to %s' %
                          (curr_class['$class_name'], curr_method['$method_name'], curr_method['$first_arg'],
                           curr_method['$rename']))
            else:
                # assuming that we are in method scope now
                if indent <= curr_method['$indent']:
                    curr_method.clear()
                    decorator = None
                    continue

                else:
                    """pat = arg_pat(curr_method['$first_arg'])
                    print(pat)
                    res = re.match(pat, line)
                    if res is None:
                        print(line)
                    print(res)
                    i += 1
                    continue"""

        if not curr_class:
            # check for class
            if line.startswith('class'):
                # extract class name
                classname = re.search(classname_pat, line).group(1)
                curr_class['$class_name'] = classname
                curr_class['$indent'] = indent
            else:
                i += 1
                continue
        i += 1


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
    run(file)
