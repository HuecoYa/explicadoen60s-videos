import json, sys
ws = json.load(open(sys.argv[1] + '_words.json'))['words']
line = []; st = None
for a, b, w in ws:
    if st is None: st = a
    line.append(w)
    if w[-1] in '.,:;?!…':
        print(f'{st:6.2f}-{b:6.2f} {" ".join(line)}'); line = []; st = None
if line: print(f'{st:6.2f} {" ".join(line)}')
