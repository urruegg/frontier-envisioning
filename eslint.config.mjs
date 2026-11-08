// ESLint flat config. The renderer is a classic browser script inlined into the blueprint HTML;
// tests are ES modules for Node. Warnings are ratcheted to errors with INT-08.
import js from "@eslint/js";
import globals from "globals";

export default [
  { ignores: ["node_modules/**", "build/**", "dist/**", "plugin/**", ".agents/**", "playwright-report/**", "test-results/**"] },
  {
    files: ["src/renderer/**/*.js"],
    languageOptions: { ecmaVersion: 2022, sourceType: "script", globals: { ...globals.browser } },
    rules: {
      ...js.configs.recommended.rules,
      "no-unused-vars": ["warn", { args: "none", caughtErrors: "none" }],
      "no-empty": ["error", { allowEmptyCatch: true }],
      "no-useless-escape": "warn",
      "no-eval": "error",
      "no-implied-eval": "error",
      "no-new-func": "error"
    }
  },
  {
    files: ["tests/**/*.mjs", "*.mjs"],
    languageOptions: { ecmaVersion: 2023, sourceType: "module", globals: { ...globals.node } },
    rules: { ...js.configs.recommended.rules }
  },
  {
    // browser tests: callbacks passed to page.evaluate run in the page
    files: ["tests/e2e/**/*.mjs"],
    languageOptions: { globals: { ...globals.node, ...globals.browser } }
  }
];
