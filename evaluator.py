import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def tokenize(expression):
    tokens=[]
    i=0
    while i<len(expression):
        char=expression[i]
        
        if char.isspace():
            i+=1
        elif char.isdigit():
            num=''
            while i<len(expression) and expression[i].isdigit():
                num+=expression[i]
                i+=1
            tokens.append(('NUM', num))
        elif char in '+-*/': 
            tokens.append(('OP', char))
            i+=1
        elif char == '(': #if the character is an opening parenthesis, we add it as a token
            tokens.append(('LPAREN', '(')) #LPAREN stands for left parenthesis
            i+=1
        elif char == ')': #if the character is a closing parenthesis, we add it as a token
            tokens.append(('RPAREN', ')')) #RPAREN stands for right parenthesis
            i+=1
        else:
            return None
    tokens.append(('END', '')) 
    return tokens

def factor(tokens, i):
    token=tokens[i]
    if token[0]=='NUM': #if the token is a number, we return its value and move to the next token
        return token[1], i+1
    elif token[0]=='LPAREN': #if the token is a left parenthesis, it skips the left parenthesis and calls the expression function to parse the expression inside the parentheses
        tree, i = expression(tokens, i+1) #we call the expression function recursively to parse the expression inside the parentheses
        i+=1 #after parsing the expression, we need to move past the right parenthesis
        return tree, i
    elif token[0]=='OP' and token[1]=='-': #if the token is a unary operator (like a negative sign), we need to parse the factor that follows it and return a tuple with the operator and the factor
        tree, i = factor(tokens, i+1) #we call the factor function recursively to parse the next factor
        return ('neg', tree), i #we return a tuple with the operator 'neg' and the parsed factor
    else:
        return 'ERROR', i #if the token is not a number, left parenthesis, or unary operator, we return an error

def term(tokens, i):
    tree, i = factor(tokens, i) #we start by parsing a factor
    while tokens[i][0]=='OP' and tokens[i][1] in '*/': #we then check for any multiplication or division operators that follow the factor
        op = tokens[i][1] #if we find an operator, we store it and move to the next token
        i+=1
        right_tree, i = factor(tokens, i) #we then parse the next factor that follows the operator
        tree = (op, tree, right_tree) #we combine the current tree with the new factor using the operator and update the tree
    return tree, i #we return the final tree and the current index

def expression(tokens, i):
    tree, i = term(tokens, i) #we start by parsing a term
    while tokens[i][0]=='OP' and tokens[i][1] in '+-': #we then check for any addition or subtraction operators that follow the term
        op = tokens[i][1] #if we find an operator, we store it and move to the next token
        i+=1
        right_tree, i = term(tokens, i) #we then parse the next term that follows the operator
        tree = (op, tree, right_tree) #we combine the current tree with the new term using the operator and update the tree
    return tree, i #we return the final tree and the current index

def evaluate(tree):
    if isinstance(tree, str): #if the tree is a string (which means it's a number), we convert it to a float and return it
        if tree == 'ERROR': #if the tree is an error, we return the error
            return 'ERROR'
        return float(tree)
    op = tree[0] #we get the operator from the tree
    if op == 'neg': #if the operator is 'neg', we evaluate the operand and return its negation
        return -evaluate(tree[1])
    #get operators and left and right subtrees
    OP=tree[0]
    left_tree=tree[1]
    right_tree=tree[2]
    if OP=='+':
        return evaluate(left_tree) + evaluate(right_tree)
    elif OP=='-': 
        return evaluate(left_tree) - evaluate(right_tree)
    elif OP=='*': 
        return evaluate(left_tree) * evaluate(right_tree)
    elif OP=='/': 
        if evaluate(right_tree)==0:
            return 'ERROR'
        else:
            return evaluate(left_tree) / evaluate(right_tree)

def format_tokens(tokens):
    result=''
    for token in tokens:
        if token[0]=='END': #if the token is an end token, we add [END] to the result
            result+='[END]'
        else:
            result+=f'[{token[0]}:{token[1]}] ' #we add the token type and value to the result with a space after
    return result.strip() #we remove any trailing whitespace

def format_tree(tree): #this function takes a parse tree and formats it as a string for easier visualization. It uses recursion to traverse the tree and format each node according to its type (number, operator, or negation).
    if isinstance(tree, str):
        return tree
    if tree[0] == 'neg':
        return f'(neg {format_tree(tree[1])})' #if the node is a negation, we format it as (neg <operand>)
    op    = tree[0]
    left  = format_tree(tree[1])
    right = format_tree(tree[2])
    return f'({op} {left} {right})'

def evaluate_file(input_path):
    output_path=os.path.join(os.path.dirname(os.path.abspath(input_path)), 'output.txt') #we create the output path by joining the directory of the input file with 'output.txt'
    result=[]
    with open(input_path, 'r') as f:
        lines = f.readlines()
    with open(output_path, 'w') as out:
        for line in lines:
            line = line.strip()
            if not line:
                continue
            tokens = tokenize(line)
            if tokens is None: #ERROR - unknown character
                out.write(f'Input: {line}\n')
                out.write('Tree: ERROR\n')
                out.write('Tokens: ERROR\n')
                out.write('Result: ERROR\n\n')
                continue
            tree, i = expression(tokens, 0)
            result = evaluate(tree)
            tree_str=format_tree(tree)
            token_str=format_tokens(tokens)
            #format result
            if result == 'ERROR': #if the result is an error, we return the error
                result_str = 'ERROR'
            elif isinstance(result, float) and result == int(result): #if the result is a whole number, we return it without the decimal point
                result_str = str(int(result))  # 8.0 → 8
            else:
                result_str = str(round(result, 4)) #otherwise we round to 4 decimal places
            out.write(f'Input: {line}\n')
            out.write(f'Tree: {tree_str}\n')
            out.write(f'Tokens: {token_str}\n')
            out.write(f'Result: {result_str}\n\n')
    return result

evaluate_file('sample_input.txt')