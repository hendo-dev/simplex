
from frac import *

"""
    Represents a stationary simplex table
    author: Hayder
    mailto: hayder_endo@icloud.com
"""
class Table:

    def __init__(self, rows_ids, cols_ids, cells):
        
        self.step = 0
        self.rows_ids = rows_ids
        self.cols_ids = cols_ids
        self.table = {}
        
        i = 0
        for row in rows_ids:
            self.table[row] = {}
            j = 0
            for col in self.cols_ids:
                self.table[row][col] = cells[i][j]
                j += 1
            i += 1
        
        
    def isOptimal(self):
        for col in self.cols_ids:
            if self.table['z'][col].lt(ZERO) and col != 'b':
                return False
        return True

    def getCurrentSolution(self):
        solution = []
        for row in self.rows_ids:
            solution.append((row, self.table[row]['b']))
        return solution
    
    def findPivotC(self):
        pivot_c = None
        colValue = ZERO

        for col in self.cols_ids:
            if col == 'b':
                continue
            value = self.table['z'][col] 
            if value.lt(colValue):
                pivot_c = col
                colValue = value
        return pivot_c

    def findPivotR(self):

        pivot_c = self.findPivotC()
        candidates = []
        for row in self.rows_ids:
            value = self.table[row][pivot_c] 
            if value.gt(ZERO):
                bj = self.table[row]['b']
                candidates.append((bj.div(value), row))
        if len(candidates) == 0:
            raise Exception('Unbounded target')
        else:
            min_val = candidates[0][0]
            min_id = candidates[0][1]
            for i in range(1,len(candidates)):
                if min_val.gt(candidates[i][0]):
                    min_val = candidates[i][0]
                    min_id = candidates[i][1]
            return min_id
    
    def next(self):
        self.step += 1
        incoming = self.findPivotC()
        outgoing = self.findPivotR()
        pivot = self.table[outgoing][incoming]

        # Updating rows_ids
        for i in range(len(self.rows_ids)):
            if self.rows_ids[i] == outgoing:
                self.rows_ids[i] = incoming
                break

        next_table = {}
        for row in self.rows_ids:
            next_table[row] = {}
        
        # Dividing pivot row by pivot value
        for col in self.cols_ids:
            next_table[incoming][col] = self.table[outgoing][col].div(pivot)

        # Updating table
        for row in self.rows_ids:
            for col in self.cols_ids:
                # Keeps the same value
                if row != incoming and col in self.rows_ids:
                    next_table[row][col] = self.table[row][col]
        
        for row in self.rows_ids:
            if row == incoming:
                next_table[row][incoming] = self.table[outgoing][outgoing]
            else:
                next_table[row][incoming] = self.table[row][outgoing]
        
        # Computing unknown values
        for row in self.rows_ids:
            # Already computed
            if row == incoming:
                continue
            for col in self.cols_ids:
                # Already computed
                if col in self.rows_ids or col == incoming:
                    continue
                # Finding value (row, col) for next table
                next_table[row][col] = self.table[row][col].sub((self.table[row][incoming].mul(self.table[outgoing][col])).div(pivot))
        self.table = next_table   


    def __str__(self):

        max_width = 0
        for row in self.rows_ids:
            max_width = max(max_width, len(str(row)))
            for col in self.cols_ids:
                max_width = max(max_width, len(str(col)), len(str(self.table[row][col])))
        
        separator = lambda how_many : '\n' + '_' * (how_many + 1) * (max_width + 1) + '\n'
        add_cell = lambda element : '|' + str(element) + (' ' * (max_width - len(str(element))))

        rep = 'Step: ' + str(self.step)
        rep += separator(len(self.cols_ids))
        
        rep += add_cell('VB')
        for col in self.cols_ids:
            rep += add_cell(col)
        rep += separator(len(self.cols_ids))

        for row in self.rows_ids:
            rep += add_cell(row)
            for col in self.cols_ids:
                rep += add_cell(self.table[row][col])
            rep += separator(len(self.cols_ids))
            
        return rep
