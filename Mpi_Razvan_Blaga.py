import os
import time
import tracemalloc
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
            'B': self._run_batch_test,
            'X': exit
        }

    def display_header(self):
        print("\u2554\u2550\u2550\u2550\u2550 CLAUSE SOLVER 9000 \u2550\u2550\u2550\u2550")

    def show_main_menu(self):
        while True:
            self._clear_screen()
            self.display_header()
            print("\nLast 10 actions:")
            for i, action in enumerate(reversed(self.history), 1):
                print(f"{i}. {action}")

            print("\nAvailable Methods:")
            print("[R]esolution   [D]avis-Putnam")
            print("[L]DPLL        [B]atch Test")
            print("E[x]it")

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
                print("Invalid option - try R, D, L, B or X")

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
        self._execute_with_metrics(self._execute_resolution, self.clauses, "RESOLUTION")

    def _run_dp(self):
        self.clauses = self._get_clauses()
        self._execute_with_metrics(self._execute_dp, self.clauses, "DP")

    def _run_dpll(self):
        self.clauses = self._get_clauses()
        print("\nChoose DPLL strategy:")
        print("1. Classic (first literal)")
        print("2. Jeroslow-Wang")
        choice = input("Select (1/2): ").strip()
        strategy = "classic" if choice == "1" else "jeroslow-wang"
        self._execute_with_metrics(lambda x: self._execute_dpll(x, strategy), self.clauses, f"DPLL ({strategy})")

    def _execute_with_metrics(self, func, clauses, label):
        tracemalloc.start()
        start = time.perf_counter()
        result = func(copy.deepcopy(clauses))
        elapsed = time.perf_counter() - start
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"\n{label} RESULT: {'SATISFIABLE' if result else 'UNSATISFIABLE'}")
        print(f"Time: {elapsed:.4f}s | Memory: {peak / 1024:.2f} KB")

    def _run_batch_test(self):
        paths = input("\nEnter CNF file paths separated by space: ").split()
        results = []
        for path in paths:
            clauses = self._parse_dimacs(path)
            for method, func in [('R', self._execute_resolution), ('D', self._execute_dp)]:
                res = self._test_case(func, clauses, method, path)
                results.append(res)
            for strategy in ['classic', 'jeroslow-wang']:
                res = self._test_case(lambda x: self._execute_dpll(x, strategy), clauses, f"L-{strategy}", path)
                results.append(res)
        self._display_results_table(results)

    def _test_case(self, func, clauses, label, file):
        tracemalloc.start()
        start = time.perf_counter()
        result = func(copy.deepcopy(clauses))
        elapsed = time.perf_counter() - start
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return {'file': file, 'method': label, 'result': 'SAT' if result else 'UNSAT', 'time': elapsed, 'memory_kb': peak / 1024}

    def _display_results_table(self, results):
        print("\nCOMPARATIVE RESULTS:")
        print(f"{'File':<20} {'Method':<15} {'Result':<10} {'Time(s)':<10} {'Memory(KB)':<12}")
        for r in results:
            print(f"{r['file']:<20} {r['method']:<15} {r['result']:<10} {r['time']:<10.4f} {r['memory_kb']:<12.2f}")

    def _parse_dimacs(self, path):
        clauses = []
        with open(path) as f:
            for line in f:
                if line.startswith('c') or line.startswith('p') or not line.strip():
                    continue
                tokens = line.strip().split()
                if tokens[-1] == '0':
                    tokens = tokens[:-1]
                clauses.append(set(tokens))
        return clauses

    def _jeroslow_wang_heuristic(self, clauses):
        score = {}
        for clause in clauses:
            for lit in clause:
                score[lit] = score.get(lit, 0.0) + (2 ** -len(clause))
        return max(score.items(), key=lambda x: x[1])[0] if score else None

    def _execute_resolution(self, K):
        k_prim = copy.deepcopy(K)
        while True:
            R = self._find_resolvent(k_prim)
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

            unit = next((C for C in k_prim if len(C) == 1), None)
            if unit:
                L = next(iter(unit))
                k_prim = self._propagate_unit(k_prim, L)
                continue

            pure = self._find_pure(k_prim)
            if pure:
                k_prim = [C for C in k_prim if pure not in C]
                continue

            return self._execute_resolution(k_prim)

    def _execute_dpll(self, K, strategy="classic"):
        k_prim = copy.deepcopy(K)
        if any(not C for C in k_prim): return False
        if not k_prim: return True

        unit = next((C for C in k_prim if len(C) == 1), None)
        if unit:
            L = next(iter(unit))
            return self._execute_dpll(self._propagate_unit(k_prim, L), strategy)

        pure = self._find_pure(k_prim)
        if pure:
            k_prim = [C for C in k_prim if pure not in C]
            return self._execute_dpll(k_prim, strategy)

        L = self._jeroslow_wang_heuristic(k_prim) if strategy == "jeroslow-wang" else next(iter(k_prim[0]))
        if not L: return True
        if self._execute_dpll(self._propagate_unit(k_prim, L), strategy):
            return True
        return self._execute_dpll(self._propagate_unit(k_prim, L[1:] if L.startswith("-") else f"-{L}"), strategy)

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

if __name__ == "__main__":
    app = SolverInterface()
    app.show_main_menu()
