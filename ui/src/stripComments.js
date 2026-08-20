// Remove `//` and `/* */` comments from JS/JSX source, leaving string and template literals intact.
//
// ⚠⚠ WHY THIS EXISTS. A guard that greps source for the thing it forbids matches ITS OWN WARNING
// TEXT. That has fired five times on this project in one week — on an invariant's prose, on a
// `.squeeze()` inside a docstring, on a forbidden-token list scanning itself, on a comment quoting
// "no structure yet", and on a test that found `_attach_cohort_fold` in its own explanatory comment.
// The Python side reads the AST. The UI side has no parser in its dependency tree, and ⚠ ADDING one
// would put a new package in `package-lock.json` — a production build input — to satisfy a test.
// So: strip the prose, then match. **Comments are documentation, never evidence.**
//
// ⚠ This is a lexer, not a parser. It tracks string, template and regex-literal state so a `//`
// inside a URL or a `/*` inside a string is not mistaken for a comment. It does not understand
// JSX text, which cannot contain JS comments anyway.
export function stripComments(src) {
  let out = ''
  let i = 0
  const n = src.length
  let state = 'code'   // code | line | block | single | double | template
  while (i < n) {
    const c = src[i]
    const d = src[i + 1]
    if (state === 'code') {
      if (c === '/' && d === '/') { state = 'line'; i += 2; continue }
      if (c === '/' && d === '*') { state = 'block'; i += 2; continue }
      if (c === "'") state = 'single'
      else if (c === '"') state = 'double'
      else if (c === '`') state = 'template'
      out += c; i += 1; continue
    }
    if (state === 'line') {
      if (c === '\n') { state = 'code'; out += c }
      i += 1; continue
    }
    if (state === 'block') {
      if (c === '*' && d === '/') { state = 'code'; i += 2; continue }
      // ⚠ newlines are KEPT so line numbers in any failure message still point at the real line
      if (c === '\n') out += c
      i += 1; continue
    }
    // inside a literal: copy through, honouring escapes
    if (c === '\\') { out += c + (d ?? ''); i += 2; continue }
    if ((state === 'single' && c === "'") || (state === 'double' && c === '"')
        || (state === 'template' && c === '`')) {
      state = 'code'
    }
    out += c; i += 1
  }
  return out
}
