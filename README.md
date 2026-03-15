Automata Forge – Natural Language to DFA Generator

Automata Forge is a Python-based system that converts natural language descriptions of formal languages into Deterministic Finite Automata (DFA). The engine analyzes textual scenarios, extracts logical constraints, constructs the corresponding DFA, minimizes it, and generates a visual diagram of the automaton.

This project demonstrates the implementation of core Theory of Computation concepts combined with rule-based natural language processing and automated visualization.

Features :
Converts natural language descriptions into formal DFA models
Extracts logical constraints using rule-based text parsing
Supports common automata constraints including:
Prefix conditions
Suffix conditions
Forbidden patterns
Even and odd occurrences
Modular arithmetic conditions
Implements DFA operations:

Construction :
Union
Intersection
DFA minimization using Hopcroft’s algorithm
Generates visual DFA diagrams using Graphviz
Allows interactive testing of input strings for acceptance or rejection

System Architecture :
User Scenario (Natural Language)
        ↓
Semantic Parsing
        ↓
Rule Extraction
        ↓
DFA Construction
        ↓
DFA Operations (Union / Intersection)
        ↓
DFA Minimization
        ↓
Graphviz Visualization
        ↓
Generated DFA Diagram

Technology Stack
Python
Libraries:-
Regular Expressions (Regex)
Graphviz
Automata Theory Algorithms
