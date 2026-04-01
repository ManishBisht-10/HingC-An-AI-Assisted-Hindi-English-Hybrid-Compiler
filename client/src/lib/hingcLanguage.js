const HINGC_LANGUAGE_ID = "hingc";

const KEYWORDS = [
  "shuru",
  "khatam",
  "rakho",
  "agar",
  "warna",
  "jabtak",
  "karo",
  "kaam",
  "wapas",
  "likho",
  "lo",
  "toro",
  "agla",
  "chunao",
  "sthiti",
  "warna_default",
];

const TYPES = ["poora", "dasha", "akshar", "shabd", "khaali"];

const LOGICAL_WORDS = ["aur", "ya", "nahi"];

const LITERALS = ["sahi", "galat"];

export function registerHingcLanguage(monaco) {
  const alreadyRegistered = monaco.languages
    .getLanguages()
    .some((lang) => lang.id === HINGC_LANGUAGE_ID);

  if (!alreadyRegistered) {
    monaco.languages.register({ id: HINGC_LANGUAGE_ID });
  }

  monaco.languages.setMonarchTokensProvider(HINGC_LANGUAGE_ID, {
    defaultToken: "",
    tokenPostfix: ".hingc",

    keywords: KEYWORDS,
    typeKeywords: TYPES,
    logicalWords: LOGICAL_WORDS,
    literalWords: LITERALS,

    operators: [
      "=",
      "+",
      "-",
      "*",
      "/",
      "%",
      ">",
      "<",
      ">=",
      "<=",
      "==",
      "!=",
      "&&",
      "||",
      "!",
      "&",
    ],

    escapes:
      /\\(?:[abfnrtv\\"'0]|x[0-9A-Fa-f]{1,2}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})/,

    tokenizer: {
      root: [
        [/warna\s+agar\b/, "keyword"],

        [/\/\*/, "comment", "@comment"],
        [/\/\/.*$/, "comment"],

        [/\b\d+\.\d+\b/, "number.float"],
        [/\b\d+\b/, "number"],
        [/"([^"\\]|\\.)*$/, "string.invalid"],
        [/"/, "string", "@string"],
        [/'([^'\\]|\\.)'/, "string"],

        [/[{}()\[\]]/, "delimiter.bracket"],
        [/[;,.:]/, "delimiter"],

        [
          /[a-zA-Z_][\w]*/,
          {
            cases: {
              "@typeKeywords": "type",
              "@logicalWords": "operator",
              "@literalWords": "constant",
              "@keywords": "keyword",
              "@default": "identifier",
            },
          },
        ],

        [/[=><!~?:&|+\-*\/%]+/, "operator"],
        [/\s+/, "white"],
      ],

      comment: [
        [/[^/*]+/, "comment"],
        [/\*\//, "comment", "@pop"],
        [/[/*]/, "comment"],
      ],

      string: [
        [/[^\\"]+/, "string"],
        [/@escapes/, "string.escape"],
        [/\\./, "string.escape.invalid"],
        [/"/, "string", "@pop"],
      ],
    },
  });

  monaco.languages.setLanguageConfiguration(HINGC_LANGUAGE_ID, {
    comments: {
      lineComment: "//",
      blockComment: ["/*", "*/"],
    },
    brackets: [
      ["{", "}"],
      ["[", "]"],
      ["(", ")"],
    ],
    autoClosingPairs: [
      { open: "{", close: "}" },
      { open: "[", close: "]" },
      { open: "(", close: ")" },
      { open: '"', close: '"' },
      { open: "'", close: "'" },
    ],
  });
}

export { HINGC_LANGUAGE_ID };
