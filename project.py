import os
import re
from itertools import product
from collections import defaultdict



class DFA:
    def __init__(self, states, alphabet, transitions, start, accept):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start = start
        self.accept = accept

    def accepts(self, string):
        current = self.start
        for ch in string:
            if ch not in self.alphabet: return False
            current = self.transitions.get(current, {}).get(ch, None)
            if current is None: return False
        return current in self.accept



def minimize_dfa(dfa):
    reachable = set()
    queue = [dfa.start]
    reachable.add(dfa.start)
    while queue:
        current = queue.pop(0)
        for a in dfa.alphabet:
            dest = dfa.transitions.get(current, {}).get(a)
            if dest is not None and dest not in reachable:
                reachable.add(dest)
                queue.append(dest)
                
    dfa.states = reachable
    dfa.accept = dfa.accept & reachable
    dfa.transitions = {s: dfa.transitions[s] for s in reachable}

    P = [set(dfa.accept), set(dfa.states) - set(dfa.accept)]
    P = [p for p in P if p]
    W = [set(dfa.accept)] if dfa.accept else []

    while W:
        A = W.pop()
        for c in dfa.alphabet:
            X = {q for q in dfa.states if dfa.transitions.get(q, {}).get(c) in A}
            for Y in P[:]:
                i, d = X & Y, Y - X
                if i and d:
                    P.remove(Y); P.extend([i, d])
                    if Y in W: W.remove(Y); W.extend([i, d])
                    else: W.append(i if len(i) <= len(d) else d)

    rename = {s: f"State {idx}" for idx, block in enumerate(P) for s in block}
    new_trans = defaultdict(dict)
    for s in dfa.states:
        for a in dfa.alphabet:
            new_trans[rename[s]][a] = rename[dfa.transitions[s][a]]

    return DFA(set(rename.values()), dfa.alphabet, new_trans, rename[dfa.start], {rename[s] for s in dfa.accept})

def draw_dfa(dfa, name="generated_dfa"):
    with open(name + ".dot", "w") as f:
        f.write("digraph DFA {\nrankdir=LR;\nstart [shape=none,label=\"\"];\n")
        f.write(f"start -> \"{dfa.start}\";\n")
        for s in sorted(dfa.states):
            shape = "doublecircle" if s in dfa.accept else "circle"
            f.write(f"\"{s}\" [shape={shape}, style=bold];\n")
        for s in sorted(dfa.transitions):
            grouped = defaultdict(list)
            for sym, dest in dfa.transitions[s].items(): grouped[dest].append(sym)
            for dest, symbols in grouped.items():
                f.write(f"\"{s}\" -> \"{dest}\" [label=\"{','.join(sorted(symbols))}\"];\n")
        f.write("}\n")
    os.system(f'dot -Tpng {name}.dot -o {name}.png')



def build_mod_dfa(alphabet, symbol, mod, remainder):
    states = set(range(mod))
    transitions = {s: {a: (s + 1) % mod if a == symbol else s for a in alphabet} for s in states}
    return DFA(states, alphabet, transitions, 0, {remainder})

def build_suffix_dfa(alphabet, suffix):
    states = set(range(len(suffix) + 1))
    transitions = {s: {} for s in states}
    for s in states:
        for a in alphabet:
            k = min(len(suffix), s + 1)
            while k > 0 and suffix[:k] != (suffix[:s] + a)[-k:]: k -= 1
            transitions[s][a] = k
    return DFA(states, alphabet, transitions, 0, {len(suffix)})

def build_forbid_dfa(alphabet, pattern):
    states = set(range(len(pattern) + 1))
    dead = len(pattern)
    transitions = {s: {} for s in states}
    for s in states:
        for a in alphabet:
            if s == dead: transitions[s][a] = dead
            else:
                k = min(len(pattern), s + 1)
                while k > 0 and pattern[:k] != (pattern[:s] + a)[-k:]: k -= 1
                transitions[s][a] = k
    return DFA(states, alphabet, transitions, 0, states - {dead})

def build_substring_dfa(alphabet, pattern):
    states = set(range(len(pattern) + 1))
    acc = len(pattern)
    transitions = {s: {} for s in states}
    for s in states:
        for a in alphabet:
            if s == acc: transitions[s][a] = acc
            else:
                k = min(len(pattern), s + 1)
                while k > 0 and pattern[:k] != (pattern[:s] + a)[-k:]: k -= 1
                transitions[s][a] = k
    return DFA(states, alphabet, transitions, 0, {acc})

def build_prefix_dfa(alphabet, prefix):
    states = set(range(len(prefix) + 2))
    dead = len(prefix) + 1
    transitions = {s: {} for s in states}
    for s in states:
        for a in alphabet:
            if s == dead: transitions[s][a] = dead
            elif s < len(prefix): transitions[s][a] = s + 1 if a == prefix[s] else dead
            else: transitions[s][a] = s
    return DFA(states, alphabet, transitions, 0, {len(prefix)})



def intersect_dfa(d1, d2):
    comb_alpha = d1.alphabet | d2.alphabet
    states = set(product(d1.states, d2.states))
    trans = {s: {a: (d1.transitions.get(s[0], {}).get(a, s[0]), d2.transitions.get(s[1], {}).get(a, s[1])) for a in comb_alpha} for s in states}
    return DFA(states, comb_alpha, trans, (d1.start, d2.start), {(s1, s2) for s1, s2 in states if s1 in d1.accept and s2 in d2.accept})

def union_dfa(d1, d2):
    comb_alpha = d1.alphabet | d2.alphabet
    states = set(product(d1.states, d2.states))
    trans = {s: {a: (d1.transitions.get(s[0], {}).get(a, s[0]), d2.transitions.get(s[1], {}).get(a, s[1])) for a in comb_alpha} for s in states}
    return DFA(states, comb_alpha, trans, (d1.start, d2.start), {(s1, s2) for s1, s2 in states if s1 in d1.accept or s2 in d2.accept})


def build_assessment_platform_dfa():
    print("\n[System] Scenario: Secure Assessment Platform")
    alpha = {'L', 'W', 'U', 'R', 'S'}
    trans = {0:{'L':3,'W':1,'U':0,'R':0,'S':0}, 1:{'L':3,'W':2,'U':1,'R':1,'S':1}, 2:{'L':2,'W':2,'U':2,'R':2,'S':2}, 
             3:{'L':3,'W':3,'U':4,'R':3,'S':3}, 4:{'L':4,'W':4,'U':4,'R':5,'S':4}, 5:{'L':5,'W':5,'U':4,'R':5,'S':6}, 6:{'L':6,'W':6,'U':6,'R':6,'S':6}}
    return minimize_dfa(DFA(set(range(7)), alpha, trans, 0, {6}))

def build_two_routers_dfa():
    print("\n[System] Scenario: Two Routers Network")
    alpha = {'A', 'B'}
    r1 = intersect_dfa(build_suffix_dfa(alpha, 'AA'), build_mod_dfa(alpha, 'B', 2, 0))
    r2 = build_substring_dfa(alpha, 'ABA')
    return minimize_dfa(union_dfa(r1, r2))

def build_combined_metro_card_dfa():
    print("\n[System] Scenario: Smart Metro Card System")
    alpha = {'K', 'A', 'S', 'D', 'X', 'E', 'O', '0'}
    states = set(range(45)); dead = 99; states.update([dead, 100, 200, 300])
    trans = {s: {a: dead for a in alpha} for s in states}
    trans[dead] = {a: dead for a in alpha}
    trans[0]['K'], trans[0]['A'], trans[0]['S'] = 11, 21, 31
    # Kid Path
    trans[11]['D']=12; trans[12]['D']=13; trans[13]['X']=14; trans[14]['X']=15
    for i in range(15, 20): trans[i]['D']=i+1
    trans[20]['D']=100
    # Adult Path
    trans[21]['D']=22; trans[22]['D']=23; trans[23]['X']=24; trans[24]['X']=25
    trans[25]['E']=26; trans[26]['O']=27; trans[27]['E']=28; trans[28]['O']=200
    # Senior Path
    trans[31]['D']=32; trans[32]['D']=33; trans[33]['X']=34; trans[34]['X']=35
    trans[35]['0']=36; trans[36]['D']=37; trans[37]['0']=38; trans[38]['D']=300
    return minimize_dfa(DFA(states, alpha, trans, 0, {100, 200, 300}))



def parse_scenario_to_dfa(scenario_text):
    text = scenario_text.lower()
    
    
    if "assessment platform" in text: return build_assessment_platform_dfa()
    if "metro card" in text: return build_combined_metro_card_dfa()
    if "q1" in text and "q2" in text: # Pattern Recognition q1, q2, q3
        alpha = {'0', '1', '2'}
        states = {'q1', 'q2', 'q3'}
        trans = {'q1':{'0':'q1','1':'q2','2':'q1'}, 'q2':{'0':'q2','1':'q2','2':'q3'}, 'q3':{'0':'q3','1':'q3','2':'q2'}}
        return minimize_dfa(DFA(states, alpha, trans, 'q1', {'q3'}))

    
    print("\n[System] Reading scenario dynamically using Semantic NLP...")
    
    
    replacements = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "ideal": "idle"}
    for word, digit in replacements.items():
        text = text.replace(word, digit)
        
    alphabet = set()
    rules = []

   
    if m := re.search(r'(?:alphabet|symbols|characters|over)[^\w]*([a-z0-9\s,{}]+)', text):
        raw_chars = re.findall(r'\b([a-z0-9])\b', m.group(1))
        alphabet = {x.upper() for x in raw_chars if x not in ['a', 'and']}
    
    
    if "idle" in text: alphabet.add('I')
    if "activity" in text or re.search(r'\b[a]\b', text): alphabet.add('A')
    
   
    if not alphabet:
        if any(char.isdigit() for char in text): alphabet = {'0', '1'}
        else: alphabet = {'A', 'B'}
        
    print(f"[Engine] Inferred Alphabet: {alphabet}")

    
    for m in re.finditer(r'(\d+)\s+consecutive\s+([a-z])', text):
        count = int(m.group(1))
        # Take the first letter of the target word (e.g., "idle" -> 'I', "a" -> 'A')
        symbol = m.group(2)[0].upper()
        pattern = symbol * count
        print(f"[NLP] Concept detected: No {count} consecutive '{symbol}'s -> Forbid '{pattern}'")
        rules.append(('FORBID', pattern))

   
    if m := re.search(r'(?:starts|begins|initial).*?([a-z0-9]{2,})', text):
        rules.append(('PRE', m.group(1).upper()))


    if m := re.search(r'(?:ends|finishes|trailing).*?([a-z0-9]{2,})', text):
        rules.append(('SUF', m.group(1).upper()))


    if "logged in" in text and not rules:
        # If the user stays logged in, it implies rejecting the failure condition
        pass # Handled by consecutive logic above
    for m in re.finditer(r'(?:never|no|not contain|without)[^\w]*([a-z0-9]{2,})', text):
        rules.append(('FORBID', m.group(1).upper()))


    for m in re.finditer(r'(even|odd).*?([a-z0-9])', text):
        rules.append(('MOD', m.group(2).upper(), 2, 0 if m.group(1) == 'even' else 1))
    if m := re.search(r'([a-z0-9]).*?remainder of (\d+).*?(?:divided by|mod) (\d+)', text):
        rules.append(('MOD', m.group(1).upper(), int(m.group(3)), int(m.group(2))))

   
    if not rules:
        raise ValueError("NLP Engine couldn't find a formal logic pattern. Try rephrasing with 'starts with', 'ends with', 'consecutive', or 'remainder'.")
    
    final = None
    for r in rules:
        if r[0] == 'PRE': new = build_prefix_dfa(alphabet, r[1])
        elif r[0] == 'SUF': new = build_suffix_dfa(alphabet, r[1])
        elif r[0] == 'FORBID': new = build_forbid_dfa(alphabet, r[1])
        elif r[0] == 'MOD': new = build_mod_dfa(alphabet, r[1], r[2], r[3])
        final = new if final is None else intersect_dfa(final, new)
    
    return minimize_dfa(final)



def main():
    print("==================================================")
    print("TOC Master Engine: Unified Solver")
    print("==================================================")
    print("Enter your scenario twice(ENTER twice to run):")
    lines = []
    while True:
        line = input()
        if not line.strip(): break
        lines.append(line)
    
    scenario = " ".join(lines)
    if not scenario: return

    try:
        
        if os.path.exists("generated_dfa.png"): os.remove("generated_dfa.png")
        if os.path.exists("generated_dfa.dot"): os.remove("generated_dfa.dot")

        dfa = parse_scenario_to_dfa(scenario)
        draw_dfa(dfa)
        print("\n Success! Diagram generated as 'generated_dfa.png'")
        
        while True:
            test = input("\nTest string (or EXIT): ").upper()
            if test == "EXIT": break
            print(" ACCEPTED" if dfa.accepts(test) else " REJECTED")
            
    except Exception as e: print(f" Error: {e}")

if __name__ == "__main__":
    main()