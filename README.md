# HingC: AI-Assisted Hindi-English Hybrid Compiler

A full-stack compiler IDE that translates HingC (Hinglish hybrid language) into equivalent C code, featuring LLM-powered error reporting and fix suggestions.

## Step 18: Deployment Documentation
To deploy the HingC compiler, follow these steps:
1. Ensure all dependencies are installed.
2. Build the project using the provided build scripts.
3. Run the compiler with the desired input files.

## Features Overview
The HingC compiler includes:
* AI-assisted error reporting.
* Suggestions for code fixes.
* Support for Hinglish syntax.

🎯 Objectives

Design a Hindi–English hybrid programming language

Implement all major phases of a compiler

Integrate an LLM to improve error handling and usability

Demonstrate practical application of compiler design concepts

Enhance beginner accessibility through intelligent feedback

🧠 System Architecture
Core Compiler Pipeline

Lexical Analysis (Flex)

Syntax Analysis (Bison/Yacc)

Semantic Analysis (Symbol Table & Type Checking)

Intermediate Code Generation

Target Code Generation (C Code)

Compilation using GCC

AI Assistance Layer (LLM)

Receives compiler error messages

Generates clear, beginner-friendly explanations

Suggests possible corrections (optional)

Explains HingC → C code translation

⚠️ The LLM acts as an auxiliary assistant and does not replace compiler logic.

🤖 Role of the LLM

The Large Language Model is used for:

Smart Error Explanation
Converts low-level compiler errors into natural language explanations.

Debugging Guidance
Helps users understand why an error occurred and how to fix it.

Code Understanding
Explains how HingC constructs are translated into C code.

(Optional Extension)
Natural language to HingC code generation.


🛠 Technologies Used
Compiler Core

C / C++

Flex (Lexical Analyzer)

Bison / Yacc (Parser)

GCC

LLM Integration

Python (integration layer)

LLM API (e.g., OpenAI or local LLM)

JSON-based communication

Development Tools

VS Code

Linux / Windows OS

