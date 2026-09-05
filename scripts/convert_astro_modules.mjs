import fs from 'fs';
import path from 'path';
import vm from 'vm';

const sourceDir = 'D:/DATA/PROJEK/agunggumelarsaputra.com/src/components/modul';
const targetDir = 'd:/DATA/PROJEK/agunggumelarsaputra-django/templates/pembelajaran/components';

if (!fs.existsSync(targetDir)) {
  fs.mkdirSync(targetDir, { recursive: true });
}

function cleanTypeScript(scriptContent) {
  let js = scriptContent;

  // 1. Remove non-null assertion operator: foo!.bar -> foo.bar, foo!( -> foo(, foo!; -> foo;
  js = js.replace(/([a-zA-Z0-9_\)\]])!(\.|\(|;|,)/g, '$1$2');

  // 2. Remove variable type annotations: const x: SomeType = ... -> const x = ...
  js = js.replace(/((?:const|let|var)\s+[a-zA-Z0-9_$]+)\s*:\s*[^=]+?(\s*=)/g, '$1$2');

  // 3. Remove 'as Type' casts
  js = js.replace(/\s+as\s+[A-Za-z0-9_|\s<>]+(?=[;\),\n])/g, '');

  // 4. Remove function parameter types: (e: MouseEvent) -> (e)
  js = js.replace(/\(([a-zA-Z0-9_$]+)\s*:\s*[A-Za-z0-9_|\s<>]+\)/g, '($1)');

  // 5. Remaining simple primitive annotations if any
  js = js.replace(/:\s*(string|number|boolean|any|void)\b/g, '');

  return js;
}

const results = [];

for (let i = 2; i <= 16; i++) {
  const sourcePath = path.join(sourceDir, `InteractiveMaterialP${i}.astro`);
  const targetPath = path.join(targetDir, `interactive_material_p${i}.html`);

  if (!fs.existsSync(sourcePath)) {
    console.error(`Missing source file: ${sourcePath}`);
    continue;
  }

  let content = fs.readFileSync(sourcePath, 'utf8');

  // Strip frontmatter
  content = content.replace(/^---[\s\S]*?---\r?\n/, '');

  // Extract and clean <script>
  content = content.replace(/<script>([\s\S]*?)<\/script>/g, (match, scriptBody) => {
    const cleanedScript = cleanTypeScript(scriptBody);

    // Validate syntax
    try {
      new vm.Script(cleanedScript);
      return `<script>\n${cleanedScript.trim()}\n</script>`;
    } catch (err) {
      console.error(`Syntax Error in P${i} script:`, err.message);
      return `<script>\n${cleanedScript.trim()}\n</script>`;
    }
  });

  fs.writeFileSync(targetPath, content.trim() + '\n', 'utf8');
  const stat = fs.statSync(targetPath);
  results.push({ module: `P${i}`, size: stat.size, file: path.basename(targetPath) });
}

console.log('Conversion results:');
console.table(results);
