Sudoku without and with SAT

Naive Constraint Solving

- Implement the naive constraint solving algorithm in the AIMA book by filling in the missing parts of the given 'sudoku.py' file. 

The naive algorithm should solve the easy puzzles quickly. It can take several minutes to solve the hard ones this way. 

Use More Pruning

- Extend the code with more advanced solving techniques as explained in [this post](http://norvig.com/sudoku.html). Create a new solver class and don't overwrite the solver from Task 1. Note that the techniques are closer to the set-based pruning, tailored to solving Sudoku. 

The advanced algorithm should now solve the hard puzzles quickly. 

Translate to SAT to Solve

- Implement an encoding of Sudoku as propositional logic formulas in conjunctive normal forms, and use a state-of-the-art SAT solver to solve. 

SAT Solvers to Use
-----

I recommend [PicoSAT](http://fmv.jku.at/picosat/) as the default choice. Go to its webpage, download, and compile (simply do `./configure.sh` and then `make`). The binary `picosat` can then take the CNF files you produce (always use extension `.cnf`). 

I highly recommend that you find a linux/mac machine to use the solver. If you have to use windows, this [note](https://gist.github.com/ConstantineLignos/4601835) may be helpful but I haven't tried. If you have difficulty in getting PicoSAT to work, try [cryptominisat](https://github.com/msoos/cryptominisat) which has more instructions about making things work on windows. 

If you want to know about more solvers, check the [page](http://www.satcompetition.org/) for the annual SAT solver competition. 

Make sure to correctly import pycosat module. I personally imported the module in pycharm