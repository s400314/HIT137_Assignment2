import os


# ================= TOKENIZER ================= #

def tokenize(expr):
    tokens = []
    i = 0

    while i < len(expr):
        c = expr[i]

        if c.isspace():
            i += 1
            continue

        if c.isdigit() or c == '.':
            num = c
            i += 1
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                num += expr[i]
                i += 1
            tokens.append(("NUM", float(num)))
            continue

        if c in "+-*/":
            tokens.append(("OP", c))
            i += 1
            continue

        if c == "(":
            tokens.append(("LPAREN", c))
            i += 1
            continue

        if c == ")":
            tokens.append(("RPAREN", c))
            i += 1
            continue

        tokens.append(("INVALID", c))
        i += 1

    tokens.append(("END", None))
    return tokens


# ================= NUMBER DISPLAY HELPER ================= #

def fmt_num(v):
    """Display a float as an integer if whole, otherwise rounded to 4dp."""
    if v == int(v):
        return str(int(v))
    return str(round(v, 4))


# ================= FORMAT TOKENS ================= #

def format_tokens(tokens):
    out = []

    for t in tokens:
        if t[0] == "NUM":
            out.append(f"[NUM:{fmt_num(t[1])}]")
        elif t[0] == "OP":
            out.append(f"[OP:{t[1]}]")
        elif t[0] == "LPAREN":
            out.append("[LPAREN:(]")
        elif t[0] == "RPAREN":
            out.append("[RPAREN:)]")
        elif t[0] == "END":
            out.append("[END]")
        else:
            return "ERROR"

    return " ".join(out)


# ================= PARSER ================= #

def parse_expression(tokens, pos):
    node, pos = parse_term(tokens, pos)

    if node == "ERROR":
        return "ERROR", pos

    while pos < len(tokens) and tokens[pos][0] == "OP" and tokens[pos][1] in "+-":
        op = tokens[pos][1]
        pos += 1
        right, pos = parse_term(tokens, pos)
        if right == "ERROR":
            return "ERROR", pos
        node = (op, node, right)

    return node, pos


def parse_term(tokens, pos):
    node, pos = parse_factor(tokens, pos)

    if node == "ERROR":
        return "ERROR", pos

    while pos < len(tokens):
        tok = tokens[pos]

        if tok[0] == "OP" and tok[1] in "*/":
            op = tok[1]
            pos += 1
            right, pos = parse_factor(tokens, pos)
            if right == "ERROR":
                return "ERROR", pos
            node = (op, node, right)

        elif tok[0] in ("NUM", "LPAREN"):
            right, pos = parse_factor(tokens, pos)
            if right == "ERROR":
                return "ERROR", pos
            node = ("*", node, right)

        else:
            break

    return node, pos


def parse_factor(tokens, pos):
    tok = tokens[pos]

    if tok[0] == "OP" and tok[1] == "-":
        pos += 1
        node, pos = parse_factor(tokens, pos)
        return ("neg", node), pos

    if tok[0] == "OP" and tok[1] == "+":
        return "ERROR", pos + 1

    if tok[0] == "LPAREN":
        pos += 1
        node, pos = parse_expression(tokens, pos)
        if node == "ERROR":
            return "ERROR", pos
        if pos < len(tokens) and tokens[pos][0] == "RPAREN":
            pos += 1
        else:
            return "ERROR", pos
        return node, pos

    if tok[0] == "NUM":
        return tok[1], pos + 1

    return "ERROR", pos + 1


# ================= EVALUATION ================= #

def eval_tree(node):
    if node == "ERROR":
        return "ERROR"

    if isinstance(node, (int, float)):
        return float(node)

    if isinstance(node, tuple):
        op = node[0]

        if op == "neg":
            val = eval_tree(node[1])
            return "ERROR" if val == "ERROR" else -val

        left = eval_tree(node[1])
        right = eval_tree(node[2])

        if left == "ERROR" or right == "ERROR":
            return "ERROR"

        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                return "ERROR"
            return left / right

    return "ERROR"


# ================= FORMAT TREE ================= #

def format_tree(node):
    if node == "ERROR":
        return "ERROR"

    if isinstance(node, (int, float)):
        return fmt_num(float(node))

    op = node[0]

    if op == "neg":
        return f"(neg {format_tree(node[1])})"

    return f"({op} {format_tree(node[1])} {format_tree(node[2])})"


# ================= FORMAT RESULT ================= #

def format_result(result):
    if result == "ERROR":
        return "ERROR"
    return fmt_num(result)


# ================= REQUIRED FUNCTION ================= #

def evaluate_file(input_path: str) -> list[dict]:
    with open(input_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    results = []
    output_lines = []

    for line in lines:
        tokens = tokenize(line)

        if any(t[0] == "INVALID" for t in tokens):
            tree_str = "ERROR"
            token_str = "ERROR"
            result = "ERROR"

        else:
            token_str = format_tokens(tokens)
            tree, pos = parse_expression(tokens, 0)

            if tree == "ERROR" or tokens[pos][0] != "END":
                tree_str = "ERROR"
                token_str = "ERROR"
                result = "ERROR"
            else:
                tree_str = format_tree(tree)
                result = eval_tree(tree)

        results.append({
            "input": line,
            "tree": tree_str,
            "tokens": token_str,
            "result": result,
        })

        output_lines.append(f"Input: {line}")
        output_lines.append(f"Tree: {tree_str}")
        output_lines.append(f"Tokens: {token_str}")
        output_lines.append(f"Result: {format_result(result)}")
        output_lines.append("")

    out_path = os.path.join(os.path.dirname(os.path.abspath(input_path)), "output.txt")
    with open(out_path, "w") as f:
        f.write("\n".join(output_lines))

    return results
