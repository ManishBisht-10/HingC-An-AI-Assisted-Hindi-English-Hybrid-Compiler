# HingC Quick Reference Guide

Fast reference for HingC language syntax and keywords.

## Program Structure

```hingc
shuru
  (* Your code here *)
khatam
```

**Required:** Every program must start with `shuru` and end with `khatam`.

---

## Variables & Types

### Declaration & Initialization

```hingc
shuru
  rakho poora x          (* Declare integer *)
  rakho poora y = 10     (* Declare and initialize *)
  rakho dasha msg = "Hi" (* String *)
  rakho akshar c = 'A'   (* Character *)
khatam
```

### Type System

| Type | Meaning | C Equivalent | Example |
|------|---------|--------------|---------|
| `poora` | Integer | `int` | `rakho poora x = 42` |
| `dasha` | String | `char*` | `rakho dasha name = "Ali"` |
| `akshar` | Character | `char` | `rakho akshar ch = 'a'` |
| `khaali` | Void/Null | `void` | `wapas` (no value) |

---

## Operators

### Arithmetic
```hingc
sum = a + b      (* Addition *)
diff = a - b     (* Subtraction *)
prod = a * b     (* Multiplication *)
quot = a / b     (* Division *)
rem = a % b      (* Modulo *)
```

### Comparison
```hingc
a == b   (* Equal *)
a != b   (* Not equal *)
a > b    (* Greater than *)
a < b    (* Less than *)
a >= b   (* Greater or equal *)
a <= b   (* Less or equal *)
```

### Logical
```hingc
aur      (* AND - both true *)
ya       (* OR - either true *)
nahi     (* NOT - reverse boolean *)

agar (x > 5 aur y < 10)    (* Both conditions *)
agar (x > 5 ya y < 10)     (* Either condition *)
agar (nahi (x == 0))       (* Not zero *)
```

---

## Control Flow

### If-Else

```hingc
shuru
  rakho poora age = 18
  
  agar (age >= 18) {
    likho("Adult\n")
  } warna {
    likho("Minor\n")
  }
  
  wapas 0
khatam
```

### While Loop

```hingc
shuru
  rakho poora i = 1
  
  jabtak (i <= 5) {
    likho("%d\n", i)
    i = i + 1
  }
  
  wapas 0
khatam
```

### For Loop

```hingc
shuru
  karo (rakho poora i = 0 ; i < 5 ; i = i + 1) {
    likho("%d\n", i)
  }
  wapas 0
khatam
```

### Break & Continue

```hingc
jabtak (i < 10) {
  agar (i == 5) {
    toro        (* Break - exit loop *)
  }
  agar (i == 3) {
    agla        (* Continue - skip to next iteration *)
  }
  i = i + 1
}
```

### Switch-Case

```hingc
shuru
  rakho poora choice = 2
  
  chunao (choice) {
    sthiti 1: likho("One\n") toro
    sthiti 2: likho("Two\n") toro
    sthiti 3: likho("Three\n") toro
    warna_default: likho("Other\n")
  }
  
  wapas 0
khatam
```

---

## Input & Output

### Print (likho)

```hingc
likho("Hello\n")              (* Simple text *)
likho("Value: %d\n", x)       (* Integer *)
likho("Name: %s\n", name)     (* String *)
likho("Char: %c\n", ch)       (* Character *)
likho("Multiple: %d %s\n", num, str)  (* Multiple values *)
```

**Format Specifiers:**
- `%d` - Integer
- `%s` - String
- `%c` - Character
- `%f` - Float (single decimal)

### Read Input (lo)

```hingc
shuru
  rakho poora age
  lo age           (* Read integer from input *)
  likho("You are %d years old\n", age)
  wapas 0
khatam
```

---

## Return Statements

```hingc
shuru
  (* Code executes *)
  wapas 0    (* Return 0 - success *)
khatam

shuru
  rakho poora x = 5
  agar (x < 0) {
    wapas 1  (* Return 1 - error *)
  }
  wapas 0
khatam
```

---

## Common Patterns

### Count to N

```hingc
shuru
  rakho poora n = 5
  karo (rakho poora i = 1; i <= n; i = i + 1) {
    likho("%d ", i)
  }
  likho("\n")
  wapas 0
khatam
```

### Sum of Numbers

```hingc
shuru
  rakho poora sum = 0
  rakho poora i = 1
  jabtak (i <= 100) {
    sum = sum + i
    i = i + 1
  }
  likho("Sum: %d\n", sum)
  wapas 0
khatam
```

### Factorial

```hingc
shuru
  rakho poora n = 5
  rakho poora fact = 1
  rakho poora i = 1
  
  jabtak (i <= n) {
    fact = fact * i
    i = i + 1
  }
  
  likho("Factorial of %d is %d\n", n, fact)
  wapas 0
khatam
```

### Check if Even/Odd

```hingc
shuru
  rakho poora num = 7
  
  agar (num % 2 == 0) {
    likho("Even\n")
  } warna {
    likho("Odd\n")
  }
  
  wapas 0
khatam
```

### Conditional Greeting

```hingc
shuru
  rakho poora hour = 14
  
  agar (hour < 12) {
    likho("Good Morning\n")
  } warna {
    agar (hour < 18) {
      likho("Good Afternoon\n")
    } warna {
      likho("Good Evening\n")
    }
  }
  
  wapas 0
khatam
```

---

## Keywords Reference

| Keyword | Function | Example |
|---------|----------|---------|
| `shuru` | Start program | `shuru` |
| `khatam` | End program | `khatam` |
| `rakho` | Declare variable | `rakho poora x = 5` |
| `poora` | Integer type | `rakho poora x` |
| `dasha` | String type | `rakho dasha s` |
| `akshar` | Character type | `rakho akshar c` |
| `agar` | If condition | `agar (condition) { }` |
| `warna` | Else clause | `} warna { }` |
| `jabtak` | While loop | `jabtak (condition) { }` |
| `karo` | For loop | `karo (init; cond; inc) { }` |
| `likho` | Print output | `likho("text\n")` |
| `lo` | Read input | `lo variable` |
| `wapas` | Return | `wapas 0` |
| `toro` | Break | `toro` |
| `agla` | Continue | `agla` |
| `chunao` | Switch | `chunao (var) { }` |
| `sthiti` | Case | `sthiti 1: ...` |
| `warna_default` | Default case | `warna_default: ...` |

---

## Reserved Operators

| Operator | Meaning | Usage |
|----------|---------|-------|
| `aur` | AND | `a aur b` |
| `ya` | OR | `a ya b` |
| `nahi` | NOT | `nahi a` |
| `+` | Add | `a + b` |
| `-` | Subtract | `a - b` |
| `*` | Multiply | `a * b` |
| `/` | Divide | `a / b` |
| `%` | Modulo | `a % b` |
| `=` | Assign | `x = 10` |
| `==` | Equal | `a == b` |
| `!=` | Not equal | `a != b` |
| `>` | Greater | `a > b` |
| `<` | Less | `a < b` |
| `>=` | Greater/equal | `a >= b` |
| `<=` | Less/equal | `a <= b` |

---

## Tips & Best Practices

### 1. Variable Naming
- Use descriptive names: `age` vs `a`
- Use lowercase with underscores: `user_name`

### 2. Comments
```hingc
(* This is a comment *)
(* Multi-line comments
   work with nested
   parentheses *)
```

### 3. String Formatting
```hingc
likho("Name: %s, Age: %d\n", name, age)  (* Good *)
likho("Name: " name ", Age: " age "\n")  (* Won't work *)
```

### 4. Return Value
- Use `wapas 0` for success
- Use `wapas 1` or other value for error

### 5. Loop Practices
```hingc
(* Good - clear loop *)
karo (rakho poora i = 0; i < 10; i = i + 1) { }

(* Avoid - infinite loop risk *)
jabtak (1) { toro }
```

---

## Common Errors & Fixes

| Error | Wrong | Right |
|-------|-------|-------|
| Missing shuru/khatam | `likho("Hi\n")` | `shuru likho("Hi\n") khatam` |
| Wrong type syntax | `rakho x poora = 5` | `rakho poora x = 5` |
| Operator missing | `agar (x > 5 y < 10)` | `agar (x > 5 aur y < 10)` |
| Extra braces | `wapas 0;` | `wapas 0` |
| Case without toro | `sthiti 1: likho("x")` | `sthiti 1: likho("x") toro` |

---

## Example Programs

### 1. Multiplication Table
```hingc
shuru
  rakho poora num = 5
  rakho poora i = 1
  
  jabtak (i <= 10) {
    likho("%d * %d = %d\n", num, i, num * i)
    i = i + 1
  }
  
  wapas 0
khatam
```

### 2. Sum and Average
```hingc
shuru
  rakho poora sum = 0
  rakho poora count = 5
  rakho poora i = 1
  
  jabtak (i <= count) {
    sum = sum + i
    i = i + 1
  }
  
  likho("Sum: %d\n", sum)
  likho("Average: %d\n", sum / count)
  
  wapas 0
khatam
```

### 3. Grade Calculator
```hingc
shuru
  rakho poora marks = 85
  
  agar (marks >= 90) {
    likho("Grade: A\n")
  } warna {
    agar (marks >= 80) {
      likho("Grade: B\n")
    } warna {
      agar (marks >= 70) {
        likho("Grade: C\n")
      } warna {
        likho("Grade: F\n")
      }
    }
  }
  
  wapas 0
khatam
```

---

## Format Specifiers Quick Reference

```
%d   - Decimal integer
%f   - Floating point
%s   - String
%c   - Character
%%   - Literal %
\n   - Newline
\t   - Tab
\\   - Backslash
```

---

## Running Your Program

### Using HingC IDE
1. Open IDE at http://localhost:5173
2. Type or paste HingC code
3. Press Ctrl+Enter to compile and run
4. View output in Output Panel

### Using API
```bash
curl -X POST http://localhost:8000/api/compile \
  -H "Content-Type: application/json" \
  -d '{"source_code":"shuru likho(\"Hello\\n\") wapas 0 khatam"}'
```

---

## Need Help?

- 📚 Full documentation: [README.md](README.md)
- 📖 Language reference: Check Examples & Docs in IDE
- 🔧 API docs: [API_DOCS.md](API_DOCS.md)
- 💡 Examples: Load from Examples drawer
- 🐛 Issues: Report on GitHub

---

**Last Updated:** 2024-01-15
**Version:** 1.0
