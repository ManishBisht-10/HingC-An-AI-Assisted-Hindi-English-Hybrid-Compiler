export const EXAMPLES = [
  {
    id: "hello_world",
    title: "Hello World",
    description: "Basic output using likho (print)",
    code: `shuru
  likho("Namaste, HingC World!\\n")
  wapas 0
khatam
`,
  },
  {
    id: "variables_arithmetic",
    title: "Variables & Arithmetic",
    description: "Declare variables and perform arithmetic operations",
    code: `shuru
  rakho poora x = 10
  rakho poora y = 5
  
  rakho poora sum = x + y
  rakho poora product = x * y
  
  likho("x = %d, y = %d\\n", x, y)
  likho("Sum: %d\\n", sum)
  likho("Product: %d\\n", product)
  
  wapas 0
khatam
`,
  },
  {
    id: "if_else",
    title: "If-Else Conditional",
    description: "Branching logic with agar (if) and warna (else)",
    code: `shuru
  rakho poora age = 18
  
  agar (age >= 18) {
    likho("Adult\\n")
  } warna {
    likho("Minor\\n")
  }
  
  wapas 0
khatam
`,
  },
  {
    id: "while_loop",
    title: "While Loop",
    description: "Iteration using jabtak (while loop)",
    code: `shuru
  rakho poora count = 1
  
  jabtak (count <= 5) {
    likho("Count: %d\\n", count)
    count = count + 1
  }
  
  likho("Done!\\n")
  wapas 0
khatam
`,
  },
  {
    id: "for_loop",
    title: "For Loop",
    description: "Iteration using karo (for loop)",
    code: `shuru
  karo (rakho poora i = 1; i <= 5; i = i + 1) {
    likho("Iteration %d\\n", i)
  }
  
  wapas 0
khatam
`,
  },
  {
    id: "switch_case",
    title: "Switch-Case",
    description: "Multi-branch decision with chunao (switch) and sthiti (case)",
    code: `shuru
  rakho poora day = 3
  
  chunao (day) {
    sthiti 1:
      likho("Monday\\n")
      toro
    sthiti 2:
      likho("Tuesday\\n")
      toro
    sthiti 3:
      likho("Wednesday\\n")
      toro
    warna_default:
      likho("Other day\\n")
  }
  
  wapas 0
khatam
`,
  },
  {
    id: "strings",
    title: "String Operations",
    description: "Working with dasha (string type)",
    code: `shuru
  rakho dasha name = "HingC"
  rakho dasha greeting = "Welcome"
  
  likho("Message: %s %s!\\n", greeting, name)
  
  wapas 0
khatam
`,
  },
  {
    id: "logical_operators",
    title: "Logical Operators",
    description: "Using aur (AND), ya (OR), and nahi (NOT)",
    code: `shuru
  rakho poora x = 10
  rakho poora y = 5
  
  agar (x > y aur x > 0) {
    likho("Both conditions true\\n")
  }
  
  agar (x < 5 ya y < 0) {
    likho("At least one true\\n")
  } warna {
    likho("Both false\\n")
  }
  
  agar (nahi (x == y)) {
    likho("x and y are different\\n")
  }
  
  wapas 0
khatam
`,
  },
  {
    id: "input_output",
    title: "Input & Output",
    description: "Using lo (input) and likho (output)",
    code: `shuru
  rakho poora number = 0
  
  likho("Enter a number: ")
  lo number
  
  likho("You entered: %d\\n", number)
  
  wapas 0
khatam
`,
  },
  {
    id: "multiplication_table",
    title: "Multiplication Table",
    description: "Nested loops to print multiplication table",
    code: `shuru
  rakho poora n = 5
  
  karo (rakho poora i = 1; i <= n; i = i + 1) {
    karo (rakho poora j = 1; j <= n; j = j + 1) {
      likho("%d ", i * j)
    }
    likho("\\n")
  }
  
  wapas 0
khatam
`,
  },
  {
    id: "factorial",
    title: "Factorial Calculation",
    description: "Calculate factorial using loops",
    code: `shuru
  rakho poora n = 5
  rakho poora factorial = 1
  rakho poora i = 1
  
  jabtak (i <= n) {
    factorial = factorial * i
    i = i + 1
  }
  
  likho("Factorial of %d is %d\\n", n, factorial)
  
  wapas 0
khatam
`,
  },
];

export const LANGUAGE_DOCS = {
  keywords: [
    { kw: "shuru", meaning: "Start function/program", example: "shuru" },
    { kw: "khatam", meaning: "End function/program", example: "khatam" },
    { kw: "rakho", meaning: "Declare variable", example: "rakho poora x = 10" },
    { kw: "poora", meaning: "Integer type", example: "rakho poora x" },
    { kw: "dasha", meaning: "String type", example: "rakho dasha msg" },
    { kw: "akshar", meaning: "Character type", example: "rakho akshar c" },
    { kw: "agar", meaning: "If statement", example: "agar (x > 5) { ... }" },
    { kw: "warna", meaning: "Else clause", example: "} warna { ... }" },
    { kw: "jabtak", meaning: "While loop", example: "jabtak (i < 10) { ... }" },
    { kw: "karo", meaning: "For loop", example: "karo (rakho poora i=0; i<10; i=i+1)" },
    { kw: "likho", meaning: "Print output", example: "likho(\"%d\\n\", x)" },
    { kw: "lo", meaning: "Read input", example: "lo x" },
    { kw: "wapas", meaning: "Return value", example: "wapas 0" },
    { kw: "toro", meaning: "Break loop", example: "toro" },
    { kw: "agla", meaning: "Continue loop", example: "agla" },
    { kw: "chunao", meaning: "Switch statement", example: "chunao (x) { ... }" },
    { kw: "sthiti", meaning: "Case label", example: "sthiti 1: ..." },
    { kw: "warna_default", meaning: "Default case", example: "warna_default: ..." },
  ],
  operators: [
    { op: "=", meaning: "Assignment", example: "x = 10" },
    { op: "+", meaning: "Addition", example: "x = a + b" },
    { op: "-", meaning: "Subtraction", example: "x = a - b" },
    { op: "*", meaning: "Multiplication", example: "x = a * b" },
    { op: "/", meaning: "Division", example: "x = a / b" },
    { op: "%", meaning: "Modulo", example: "x = a % b" },
    { op: ">", meaning: "Greater than", example: "if (x > 5)" },
    { op: "<", meaning: "Less than", example: "if (x < 5)" },
    { op: "==", meaning: "Equal to", example: "if (x == 5)" },
    { op: "!=", meaning: "Not equal", example: "if (x != 5)" },
    { op: ">=", meaning: "Greater or equal", example: "if (x >= 5)" },
    { op: "<=", meaning: "Less or equal", example: "if (x <= 5)" },
    { op: "aur", meaning: "Logical AND", example: "if (x > 0 aur y > 0)" },
    { op: "ya", meaning: "Logical OR", example: "if (x > 0 ya y > 0)" },
    { op: "nahi", meaning: "Logical NOT", example: "if (nahi x)" },
  ],
  tips: [
    "Every HingC program must start with 'shuru' and end with 'khatam'",
    "Use likho for output, similar to printf in C",
    "Use lo for input, similar to scanf in C",
    "Variable types: poora (int), dasha (string), akshar (char)",
    "All statements should end naturally or with proper closing braces",
    "Indentation is for readability; proper braces are required",
  ],
};
