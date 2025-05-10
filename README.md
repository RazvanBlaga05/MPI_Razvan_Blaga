# MPI_Razvan_Blaga
This repository contains my project on solving the SAT (Boolean satisfiability) problem using several classical algorithms.

## Project Structure
Mpi_Razvan_Blaga.py – contains the full implementation, including the interactive CLI

.cnf files – SAT instances in DIMACS format (add your test files)

README.md – project overview and usage guide

## Features
Resolution: standard implementation of the classical resolution method based on clause pair processing.

Davis–Putnam (DP): includes unit clause propagation and pure literal elimination to simplify clause sets.

DPLL: Davis–Putnam–Logemann–Loveland algorithm, with two branching strategies:

Classic: picks the first literal available

Jeroslow–Wang: uses a frequency-based heuristic to guide decisions

Batch Testing involves running all three algorithms on multiple CNF files at once and collecting performance data (runtime and memory usage).

# How to use

## Option 1: Manual Clause Input
Run main.py

Choose an algorithm from the main menu (R, D, or L)

Enter each clause on a new line, separating literals with spaces (e.g. A -B C)

Press Enter twice to signal the end of input

Results, including SAT/UNSAT and performance metrics, will be displayed

## Option 2: Run Batch Tests
Run main.py

Choose option B (Batch Test)

Input one or more paths to .cnf files, separated by spaces

The program will run each method on each file and display a comparison table of results
