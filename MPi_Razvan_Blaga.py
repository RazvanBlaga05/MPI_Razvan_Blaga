import os
import copy
from collections import deque

class SolverInterface:
    def __init__(self):
        self.clauses = []
        self.history = deque(maxlen=10)
        self.methods = {
            'R': self._run_resolution,
            'D': self._run_dp,
            'L': self._run_dpll,
            'X': exit
        }

    def display_header(self):
        print("╔════════════════════════════╗")
        print("║  CLAUSE SOLVER 9000        ║")
        print("╚════════════════════════════╝")

    def show_main_menu(self):
        while True:
            self._clear_screen()
            self.display_header()
            print("\nLast 10 actions:")
            for i, action in enumerate(reversed(self.history), 1):
                print(f"{i}. {action}")
            
            print("\nAvailable Methods:")
            print("[R]esolution   [D]avis-Putnam")
            print("[L]DPLL        E[x]it")
            
            choice = input("\nSelect operation: ").upper()
            self.history.append(f"Selected: {choice}")
            
            if choice in self.methods:
                if choice == 'X':
                    print("Goodbye!")
                    break
                self.methods[choice]()
                input("\nPress any key to continue...")
            else:
                self.history.append("Invalid selection!")
                print("Invalid option - try R, D, L, or X")

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _get_clauses(self):
        print("\nEnter clauses (space-separated literals):")
        print("Press enter twice to finish\n")
        clauses = []
        while True:
            line = input("Clause> ").strip()
            if not line:
                if clauses:
                    break
                else:
                    continue
            clauses.append(set(line.split()))
        return clauses

    def _run_resolution(self):
        self.clauses = self._get_clauses()
        result = self._execute_resolution(self.clauses)
        print("\nRESOLUTION RESULT:", "SATISFIABLE" if result else "UNSATISFIABLE")

    def _run_dp(self):
        self.clauses = self._get_clauses()
        result = self._execute_dp(self.clauses)
        print("\nDP RESULT:", "SATISFIABLE" if result else "UNSATISFIABLE")

    def _run_dpll(self):
        self.clauses = self._get_clauses()
        result = self._execute_dpll(self.clauses)
        print("\nDPLL RESULT:", "SATISFIABLE" if result else "UNSATISFIABLE")

    # The actual solving methods remain identical to original functionality
    def _execute_resolution(self, K):
        k_prim = copy.deepcopy(K)
        cont = 1
        while True:
            R = self._find_resolvent(k_prim)
            print(f"\nStep {cont}")
            cont += 1
            print("Resolvent:", R)
            if R is None: return True  
            if R == set(): return False
            k_prim.append(R)

    def _find_resolvent(self, K):
        for i in range(len(K)-1):
            for j in range(i+1, len(K)):
                R = self._make_resolvent(K[i], K[j])
                if R is not None and R not in K:
                    return R
        return None

    def _make_resolvent(self, c1, c2):
        for lit in c1:
            comp = lit[1:] if lit.startswith("-") else f"-{lit}"
            if comp in c2:
                R = [x for x in c1 if x != lit] + [y for y in c2 if y != comp]
                return set(R) if R else set()
        return None

    def _execute_dp(self, K):
        k_prim = copy.deepcopy(K)
        while True:
            if k_prim is None: return True
            if any(not C for C in k_prim): return False
            
            unit = next((C for C in k_prim if len(C)==1), None)
            if unit:
                L = next(iter(unit))
                print(f"\nUnit propagate: {L}")
                k_prim = self._propagate_unit(k_prim, L)
                print("Clauses:", k_prim)
                continue
            
            pure = self._find_pure(k_prim)
            if pure:
                print(f"\nPure literal: {pure}")
                k_prim = [C for C in k_prim if pure not in C]
                print("Clauses:", k_prim)
                continue
            
            return self._execute_resolution(k_prim)

    def _propagate_unit(self, clauses, L):
        comp = L[1:] if L.startswith("-") else f"-{L}"
        new_clauses = []
        for C in clauses:
            if L in C: continue
            if comp in C:
                new = C.copy()
                new.remove(comp)
                new_clauses.append(new)
            else:
                new_clauses.append(C)
        return new_clauses

    def _find_pure(self, clauses):
        literals = {lit for clause in clauses for lit in clause}
        for lit in literals:
            comp = lit[1:] if lit.startswith("-") else f"-{lit}"
            if comp not in literals:
                return lit
        return None

    def _execute_dpll(self, K):
        k_prim = copy.deepcopy(K)
        while True:
            if k_prim is None: return True
            if any(not C for C in k_prim): return False
            
            unit = next((C for C in k_prim if len(C)==1), None)
            if unit:
                L = next(iter(unit))
                print(f"\nUnit propagate: {L}")
                k_prim = self._propagate_unit(k_prim, L)
                print("Clauses:", k_prim)
                continue
            
            pure = self._find_pure(k_prim)
            if pure:
                print(f"\nPure literal: {pure}")
                k_prim = [C for C in k_prim if pure not in C]
                print("Clauses:", k_prim)
                continue
            
            if not k_prim: return True
            
            L = next(iter(k_prim[0]))
            print(f"\nBranching on: {L}")
            if self._execute_dpll(self._propagate_unit(k_prim.copy(), L)):
                return True
            print(f"\nBranching on: ¬{L}")
            return self._execute_dpll(self._propagate_unit(k_prim.copy(), 
                L[1:] if L.startswith("-") else f"-{L}"))

if __name__ == "__main__":
    app = SolverInterface()
    app.show_main_menu()