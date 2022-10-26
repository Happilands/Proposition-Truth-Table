import itertools

class Operation:
    def __init__(self, character: str, priority: int, function, left: bool = True, right: bool = True, reverseOrder: bool = False):
        self.character = character
        self.priority = priority
        self.function = function
        self.left = left
        self.right = right
        self.reverseOrder = reverseOrder

class PropositionSolver():
    def __init__(self):
        self.operations = []
        pass

    def AddOperation(self, operation: Operation):
        self.operations.append(operation)

    def Initialize(self):
        self.opChars = ['(', ')', ' ']
        for op in self.operations:
            self.opChars.append(op.character)

    def GetProposition(self):
        self.proposition = input("Enter a logical statement:\n")

    def Parse(self):
        # Setup
        self.args = []
        self.vars = []

        varBegin = 0
        i = 0

        # Parse Arguments into args[] and vars[]
        for c in self.proposition:
            if(self.opChars.__contains__(c)):
                if(i > varBegin):
                    var = self.proposition[varBegin:i]
                    self.vars.append(var)
                    self.args.append(var)
                self.args.append(c)
                varBegin = i + 1
            i += 1
        
        if(i > varBegin):
            var = self.proposition[varBegin:i]
            self.vars.append(var)
            self.args.append(var)

        # Throw out duplicates and sort vars lexicographically
        sortedVars = list(set(self.vars))
        sortedVars.sort()
        self.vars = sortedVars

        # Replace var strings by an index to the unique var list
        i = -1
        for arg in self.args:
            i += 1
            if(self.vars.__contains__(arg)):
                self.args[i] = self.vars.index(arg)

    def InitTruthTable(self):
        self.table = []

        self.table.append(self.vars)
        self.table.append("-" * len(self.vars))

        # Binary Variables
        for b in map(''.join, itertools.product('01', repeat=len(self.vars))):
            self.table.append(list(b))

    def DrawTruthTable(self):
        # Make format and remove parentheses from varStrings  
        i = -1
        for var in self.vars:
            i += 1
            breakPar = True
            j = -1
            for char in var:
                j += 1
                if(char == ')' and j != len(var) - 1):
                    breakPar = False
            if(breakPar and var[0] == '(' and var[-1] == ")"):
                self.vars[i] = var[1:-1]

        format = "| "
        for var in self.vars:
            format += "{:<" + str(len(var) + 1) + "}| "

        print("\nTruth Table:")
        for row in self.table:
            print (format.format(*row))

    def DoOperation(self, argIndex, operation, firstP, lastP):

        opString = ""
        leftVarIndex = -1
        rightVarIndex = -1

        # Add parentheses to varString if operation is the last in its scope
        addParentheses = (argIndex - operation.left == firstP and argIndex + operation.right + 1 == lastP and firstP != 0)

        if(addParentheses): opString += "("

        if(operation.left):
            if(argIndex <= firstP):
                raise Exception("Error: No argument left of operation '" + self.args[argIndex] + "'")
            leftVarIndex = int(self.args[argIndex - 1])
            opString += self.vars[leftVarIndex]
        opString += self.args[argIndex]
        if(operation.right):
            if(argIndex + 1 >= lastP):
                raise Exception("Error: No argument right of operation '" + self.args[argIndex] + "'")
            rightVarIndex = int(self.args[argIndex + 1])
            opString += self.vars[rightVarIndex]

        if(addParentheses): opString += ")"

        self.vars.append(opString)
        self.table[1] += "-"

        # Calculations

        for i in range(2, len(self.table)):
            left = None
            right = None

            if(operation.left):
                left = int(self.table[i][leftVarIndex])
            if(operation.right):
                right = int(self.table[i][rightVarIndex])

            self.table[i].append(operation.function(left, right))

        self.args[argIndex] = len(self.vars) - 1
        if(operation.right):
            del self.args[argIndex + 1]
        if(operation.left):
            del self.args[argIndex - 1]
        return True

    def FindOperation(self):
        if(len(self.args) == 1):
            return False

        # Find the first pair of parentheses
        lastP = 0
        firstP = 0
        for arg in self.args:
            if(arg == '('):
                firstP = lastP + 1
            elif(arg == ')'):
                break
            lastP += 1

        if(lastP - firstP == 1):
            del self.args[lastP]
            del self.args[firstP - 1]
            return True

        opPriority = 99999999999
        opArgIndex = -1
        opOperation = None
        i = firstP
        while(i < lastP):
            for op in self.operations:
                if(op.character == self.args[i]):
                    if  (op.priority < opPriority or (op.priority == opPriority and op.reverseOrder)):
                        opPriority = op.priority
                        opArgIndex = i
                        opOperation = op
            i += 1

        return self.DoOperation(opArgIndex, opOperation, firstP, lastP)

    def ParseParentheses(self):
        parentheses = 0
        for arg in self.args:
            if(arg == "("):
                parentheses += 1
            elif(arg == ")"):
                parentheses -= 1
            
            if(parentheses < 0):
                raise Exception("Error: Unmatched ')'")
        if(parentheses > 0):
            raise Exception("Error: Unmatched '('")
        return True

    def Solve(self):
        self.Parse()

        if(not(self.ParseParentheses())):
            return False

        self.InitTruthTable()
        while(self.FindOperation()):
            pass

        self.DrawTruthTable()
        return True


if(__name__ == '__main__'):
    solver = PropositionSolver()

    def Negation(a: bool, b: bool): return not(b)
    def Conjunction(a: bool, b: bool): return (a and b)
    def Disjunction(a: bool, b: bool): return (a or b)
    def Implication(a: bool, b: bool): 
        if not(a): return True 
        else: return b
    def Causation(a: bool, b: bool): 
        if not(b): return True 
        else: return a
    def Equality(a: bool, b: bool): return a==b
    def Inequality(a: bool, b: bool): return a!=b

    solver.AddOperation(Operation('!', 0, Negation, False, True))
    solver.AddOperation(Operation('^', 1, Conjunction))
    solver.AddOperation(Operation('|', 2, Disjunction))
    solver.AddOperation(Operation('>', 3, Implication, True, True, True)) # Reverse order operations
    solver.AddOperation(Operation('<', 3, Causation))
    solver.AddOperation(Operation('=', 4, Equality))
    solver.AddOperation(Operation('/', 4, Inequality))

    print("\
--Operations--\n\
Negation:       !\n\
Conjunction:    ^\n\
Disjunction:    |\n\
Implication:    >\n\
Causation:      <\n\
Equality:       =\n\
Inequality:     /\n\
Sequencing:    ( )\n\
")

    solver.Initialize()
    solver.GetProposition()

    try: solver.Solve()
    except Exception as e: print(e)
