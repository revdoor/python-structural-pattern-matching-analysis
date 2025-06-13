# Python Structural Pattern Matching Analysis

## Goal

Analyse the structural pattern matching in the given code,
and give an analysis of the code.

It provides an analysis of the useless patterns, as well as non-exhaustive matches.  
For the useful patterns, it also provides some example values that match with the pattern.  
For the non-exhaustive matches, it provides some example values that is not covered with the pattern.

## Requirements

- Python 3.10 or later (for structural pattern matching)
- z3 module for finding test cases

## Usage

```
python analyze.py -t <target_file>
```

For example, if run the code with 'test.py', then the output will be:

```
Checking pattern matching in line 2:
* L3 pattern is useful
 x: 1  y: 2 
* L5 pattern is useful
 x: 2  y: 3 
* L7 pattern is useful
 x: ""  y: 2 
! L9 pattern is useless. (It does not match any cases)
* L11 pattern is useful
 x: 3  y: 3 
* L13 pattern is useful
 x: 3  y: 4 
The match is non-exhaustive. There are patterns that are not covered by the match cases.
Check cases such as:
 x: 5  y: True 

Checking pattern matching in line 16:
* L17 pattern is useful
 x: 1 
* L19 pattern is useful
 x: 3 
! L21 pattern is useless. (It does not match any cases)
* L23 pattern is useful
 x: 4 
The match is exhaustive. All possible patterns are covered by the match cases.
```

## TODO

- Need to handle the pattern guards as well as custom classes.

### ETC

This repository is for team assignment in the course "CS453 Automated Software Testing" in 2025 Spring at KAIST.