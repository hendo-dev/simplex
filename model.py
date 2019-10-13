from simplex_table import Table
from bound import Bound
from frac import *

"""
    Represents a model
    author: Hayder
    mailto: hayder_endo@icloud.com
"""

class Model:

    def __init__(self, target, bounds):

        self.target = target
        self.bounds = bounds
        self.fake_vars = set()
        self.slak_vars = set()
        self.surplus_vars = set()
        self.init_vars = set()
        self.free_vars = set()
        self.pending_vars = {}
        self.type_changed = False

        for pair in target.pairs:
            self.init_vars.add(pair)

        for bound in self.bounds:
            for pair in bound.pairs:
                self.init_vars.add(pair)

        bounded = set()
        for bound in self.bounds:
            if bound.non_neg:
                only = bound.pairs.popitem()
                bounded.add(only[0])
                bound.pairs[only[0]] = only[1]

        self.free_vars = self.init_vars.difference(bounded)


    def solve(self):

        self.assertOrResolveFreedom()

        if self.isBasic():

            last_used_id = len(self.init_vars) + 1
            new_bounds = []
            for bound in self.bounds:
                if bound.non_neg:
                    continue
                name = 'x' + str(last_used_id)
                self.slak_vars.add(name)
                bound.pairs[name] = ONE
                new_bounds.append(Bound({name : ONE}, '>=', ZERO, True))
                last_used_id += 1
            self.bounds += new_bounds
            cols_ids = sorted(self.init_vars.union(self.slak_vars))
            cols_ids.append('b')
            rows_ids = sorted(self.slak_vars)
            rows_ids.insert(0, 'z')
            cells = [ [ZERO for i in range(len(cols_ids))] for j in range(len(rows_ids)) ]
            row = 0
            
            for pair in self.target.pairs:
                col = cols_ids.index(pair)
                cells[row][col] = self.target.pairs[pair].mul(MONE)
            
            row += 1
            for bound in self.bounds:
                if bound.non_neg:
                    continue
                for pair in bound.pairs:
                    col = cols_ids.index(pair)
                    cells[row][col] = bound.pairs[pair]
                cells[row][-1] = bound.b
                row += 1

            solution = Table(rows_ids, cols_ids, cells)

            while not solution.isOptimal():
                print(solution)
                solution.next()
            print(solution)

            final_solution = solution.getCurrentSolution()
            self.printSolution(final_solution)

        else:
            # Non-basic model -> needs reconfiguration

            # Change min -> max
            if self.target.kind.upper() != 'MAX' and not self.type_changed:
                for pair in self.target.pairs:
                    self.target.pairs[pair] = self.target.pairs[pair].mul(MONE)
                self.type_changed = True
                self.solve()
                return

            # Negative bj
            if not self.areBoundsOk():
                self.fixBounds()
                self.solve()
                return
            
            # Slak vars
            last_used_id = len(self.init_vars) + 1
            newBounds = []
            
            for bound in self.bounds:
                if not bound.non_neg and bound.kind == '<=':
                    new_id = 'xh' + str(last_used_id) 
                    self.slak_vars.add(new_id)
                    bound.pairs[new_id] = ONE
                    newBounds.append(Bound({new_id : ONE}, '>=', ZERO, True))
                    last_used_id += 1

            # Surplus vars
            self.bounds += newBounds
            newBounds = []

            for bound in self.bounds:
                if not bound.non_neg and bound.kind.count('>') > 0:
                    new_id = 'xi' + str(last_used_id)
                    self.surplus_vars.add(new_id)
                    bound.pairs[new_id] = MONE
                    newBounds.append(Bound({new_id : ONE},'>=', ZERO, True))
                    last_used_id += 1
            
            self.bounds += newBounds

            # Fake vars
            newBounds = []
            for bound in self.bounds:
                if not bound.non_neg and bound.kind != '<=' and bound.kind.count('=') >= 0:
                    new_id = 'xt' + str(last_used_id)
                    self.fake_vars.add(new_id)
                    bound.pairs[new_id] = ONE
                    newBounds.append(Bound({new_id : ONE}, '>=', ZERO, True))
                    last_used_id += 1
            
            self.bounds += newBounds

            # SIMPLEX PHASE 1

            cols_ids = sorted(self.init_vars.union(self.surplus_vars).union(self.fake_vars).union(self.slak_vars))
            cols_ids.append('b')
            rows_ids = sorted(self.slak_vars.union(self.fake_vars))
            rows_ids.insert(0, 'z')

            cells = [ [ZERO for i in range(len(cols_ids))] for j in range(len(rows_ids)) ]

            row = 0
            for fake in self.fake_vars:
                col = cols_ids.index(fake)
                cells[row][col] = ONE
            
            row += 1
            for bound in self.bounds:
                if bound.non_neg:
                    continue
                for pair in bound.pairs:
                    col = cols_ids.index(pair)
                    cells[row][col] = bound.pairs[pair]
                cells[row][-1] = bound.b
                row += 1

            # Updating z row
            delta = [ZERO for i in range(len(cols_ids))]
            for var in self.fake_vars:
                row = rows_ids.index(var)
                for i in range(len(cols_ids)):
                    delta[i] = delta[i].add(cells[row][i])
            
            for col in range(len(cols_ids)):
                cells[0][col] = cells[0][col].sub(delta[col])

            print('Phase 1:')
            table = Table(rows_ids, cols_ids, cells)
            while not table.isOptimal():
                print(table)
                table.next()
            print(table)

            for var in table.rows_ids:
               if var in self.fake_vars:
                   raise Exception('Original problem has no solution')
            
            # SIMPLEX PHASE 2

            # Removing unused cols
            ids = sorted(self.fake_vars)
            first = table.cols_ids.index(ids[0])

            new_tab = {}
            for row in table.rows_ids:
                new_tab[row] = {}
                for col in table.cols_ids:
                    if col in ids:
                        continue
                    new_tab[row][col] = ZERO

            for i in range(1,len(table.rows_ids)):
                row = table.rows_ids[i]
                for j in range(len(table.cols_ids) - len(ids)):
                    col = table.cols_ids[j]
                    new_tab[row][col] = table.table[row][col]
                new_tab[row]['b'] = table.table[row]['b']

            for i in range(len(ids)):
                table.cols_ids.pop(first)

            table.table = new_tab
            
            # Updating z row

            for pair in self.target.pairs:
                new_tab['z'][pair] = self.target.pairs[pair].mul(MONE)
            
            
            delta = [ZERO for i in range(len(table.cols_ids))]
 
            for row in self.init_vars:
                coef = new_tab['z'][row]
                if new_tab.get(row) is not None:
                    for i in range(len(table.cols_ids)):
                        delta[i] = delta[i].add(coef.mul(new_tab[row][table.cols_ids[i]])) 

            for col in range(len(table.cols_ids)):
                new_tab['z'][table.cols_ids[col]] = new_tab['z'][table.cols_ids[col]].sub(delta[col])
            
            print('Phase 2')
            table.step = 0
            while not table.isOptimal():
                print(table)
                table.next()
            print(table)
            final_solution = table.getCurrentSolution()
            
            self.printSolution(final_solution)

        

    def isBasic(self):

        if self.target.kind.upper() != 'MAX' and not self.type_changed:
            return False

        for bound in self.bounds:
            if bound.kind != '<=' and not bound.non_neg:
                return False
        return True
        

    def printSolution(self, final_solution):
        
        ignore = set()
        if len(self.pending_vars) > 0:
            
            new_final_solution = []
            for pending in self.pending_vars:

                ignore.add(self.pending_vars[pending][0])
                ignore.add(self.pending_vars[pending][1])

                one = self.pending_vars[pending][0]
                other = self.pending_vars[pending][1]
                    
                for sol in final_solution:
                    if sol[0] == one:
                        one = sol[1]
                    elif sol[0] == other:
                        other = sol[1]

                # If any not in BV value 0 is set
                if type(one) == str:
                    one = ZERO
                if type(other) == str:
                    other = ZERO
                new_final_solution.append((pending, one.sub(other)))

            for sol in final_solution:
                if sol[0] in ignore or sol[0] == 'z':
                    continue
                new_final_solution.append(sol)
            
            new_final_solution.insert(0, ('z', final_solution[0][1]))
            final_solution = new_final_solution

        if self.target.kind.upper() == 'MIN':
            final_solution[0] = ('z', final_solution[0][1].mul(MONE))
            
        for i in range(len(final_solution)):
            final_solution[i] = (final_solution[i][0], str(final_solution[i][1]))

        # Missing initial vars
        ids_so_far = [ sol[0] for sol in final_solution ]
        new_ones = []
        
        for var in self.init_vars:
            if var not in ids_so_far and var not in ignore:
                new_ones.append((var, str(ZERO)))
        
        final_solution += new_ones
        final_solution = sorted(final_solution)
        
        print('Solution: ')
        for sol in final_solution:
            print(sol[0],'=',sol[1])       

    def areBoundsOk(self):

        for bound in self.bounds:
            if bound.b.lt(ZERO):
                return False
        return True

    def fixBounds(self):

        for bound in self.bounds:
            if bound.b.lt(ZERO):
                for pair in bound.pairs:
                    bounds.pairs[pair] = bounds.pairs[pair].mul(MONE)
                    # Changing sign
                    if bound.kind == '<=':
                        bound.kind = '>='
                    elif bound.kind == '>=':
                        bound.kind = '<='
                    elif bound.kind == '>':
                        bound.kind = '<'
                    elif bound.kind == '<':
                        bound.kind = '>'

    def assertOrResolveFreedom(self):
        
        if len(self.free_vars) == 0:
            return

        newBounds = []
        free_vars = self.free_vars

        last_used_id = len(self.init_vars.union(self.fake_vars).union(self.free_vars).union(self.slak_vars)) + 1

        for free in free_vars:
            self.init_vars.discard(free)
            # New representation
            id1 = 'x' + str(last_used_id)
            self.init_vars.add(id1)
            last_used_id += 1
            id2 = 'x' + str(last_used_id)
            coef = self.target.pairs.pop(free)
            self.target.pairs[id1] = coef
            self.target.pairs[id2] = coef.mul(MONE)
            self.init_vars.add(id2)
            last_used_id += 1
            newBounds.append(Bound({id1 : ONE}, '>=', ZERO, True))
            newBounds.append(Bound({id2 : ONE}, '>=', ZERO, True))
            self.pending_vars[free] = (id1, id2)
            for bound in self.bounds:
                if not bound.non_neg and bound.pairs.get(free) is not None:
                    coef = bound.pairs[free]
                    bound.pairs.pop(free)
                    bound.pairs[id1] = coef
                    bound.pairs[id2] = coef.mul(MONE)            
            self.bounds += newBounds
        
        self.free_vars = set()