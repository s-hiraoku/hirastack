#!/usr/bin/env node
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { mkdtempSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { tmpdir } from "node:os";

const target = resolve(process.argv[2]);
const ts = createRequire(join(target, "package.json"))("typescript");
const allowedShared = new Set(["src/protocol.ts", "src/security.ts"]);

function inspect(root, entries) {
  const pending = [...entries], seen = new Set(), edges = [];
  while (pending.length) {
    const name = pending.pop();
    if (seen.has(name)) continue;
    seen.add(name);
    assert(name.startsWith("src/relay/") || allowedShared.has(name), `forbidden communication dependency: ${name}`);
    const source = ts.createSourceFile(name, readFileSync(join(root, name), "utf8"), ts.ScriptTarget.Latest, true);
    assert.equal(source.parseDiagnostics.length, 0, `cannot parse: ${name}`);
    const dependency = (specifier) => {
      assert(ts.isStringLiteralLike(specifier), `computed module path requires review: ${name}`);
      const value = specifier.text;
      edges.push({ from: name, to: value });
      if (value.startsWith(".")) {
        const next = relative(root, resolve(root, dirname(name), value));
        assert(next.endsWith(".ts"), `unresolved project module: ${next}`);
        pending.push(next);
      } else {
        assert(value.startsWith("node:") || value === "zod" || value.startsWith("@modelcontextprotocol/"), `unreviewed package dependency: ${value}`);
      }
    };
    const visit = (node) => {
      if ((ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) && node.moduleSpecifier) dependency(node.moduleSpecifier);
      if (ts.isImportEqualsDeclaration(node) && ts.isExternalModuleReference(node.moduleReference)) dependency(node.moduleReference.expression);
      if (ts.isImportTypeNode(node) && ts.isLiteralTypeNode(node.argument)) dependency(node.argument.literal);
      if (ts.isCallExpression(node) && (node.expression.kind === ts.SyntaxKind.ImportKeyword || (ts.isIdentifier(node.expression) && node.expression.text === "require"))) {
        assert.equal(node.arguments.length, 1, `unknown loader shape: ${name}`);
        dependency(node.arguments[0]);
      }
      ts.forEachChild(node, visit);
    };
    visit(source);
  }
  return { files: [...seen].sort(), edges };
}

if (process.argv.includes("--self-test")) {
  const scratch = mkdtempSync(join(tmpdir(), "hirastack-boundary-"));
  try {
    mkdirSync(join(scratch, "src/relay"), { recursive: true });
    const entry = join(scratch, "src/relay/index.ts");
    writeFileSync(entry, "// Hermes and Task are allowed words in comments.\nexport const x = 'openai';\n");
    assert.equal(inspect(scratch, ["src/relay/index.ts"]).files.length, 1);
    for (const text of [
      'import "../hermes-run-driver.ts";',
      'export * from "../generic-jobs.ts";',
      'import OpenAI from "openai";',
      'const x = import(process.env.PRODUCT);',
      'import X = require("../hermes-run-driver.ts");',
    ]) {
      writeFileSync(entry, text);
      assert.throws(() => inspect(scratch, ["src/relay/index.ts"]));
    }
    writeFileSync(entry, 'import "./helper.ts";');
    writeFileSync(join(scratch, "src/relay/helper.ts"), 'export * from "../generic-jobs.ts";');
    assert.throws(() => inspect(scratch, ["src/relay/index.ts"]));
    console.log(JSON.stringify({ status: "pass", negativeControls: 6, commentAndStringFalsePositiveControl: "pass" }));
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
} else {
  const entries = readdirSync(join(target, "src/relay")).filter((name) => name.endsWith(".ts")).map((name) => `src/relay/${name}`);
  assert(entries.length > 0, "empty communication source set");
  console.log(JSON.stringify({ status: "pass", ...inspect(target, entries), limits: "AST module edges only, including type imports; not reflection, runtime capabilities or dependencies inside npm packages." }, null, 2));
}
