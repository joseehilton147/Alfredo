from pathlib import Path
import markdown

def md_to_html(md_path: Path, css_path: Path = None, title: str = None) -> Path:
    """Converte um arquivo .md para .html estilizado. Retorna o caminho do .html gerado."""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'fenced_code', 'tables', 'toc', 'codehilite', 'sane_lists', 'smarty'
        ]
    )
    # CSS moderno com dark mode toggle
    css = '''<style>
body {
  max-width: 800px;
  margin: 2em auto;
  font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  background: #f9f9f9;
  color: #222;
  padding: 2em;
  line-height: 1.7;
  font-size: 1.1em;
  transition: background 0.3s, color 0.3s;
}
h1, h2, h3, h4 {
  color: #2a5d9f;
  margin-top: 2em;
}
pre, code {
  background: #eee;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Mono', 'Consolas', monospace;
  font-size: 1em;
}
pre {
  padding: 1em;
  overflow-x: auto;
}
blockquote {
  border-left: 4px solid #2a5d9f;
  padding-left: 1em;
  color: #555;
  background: #f3f7fa;
}
hr {
  border: 0;
  border-top: 1px solid #ccc;
  margin: 2em 0;
}
a {
  color: #2a5d9f;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
ul, ol {
  margin-left: 2em;
}
li {
  margin-bottom: 0.5em;
}
/* Dark mode */
body.dark {
  background: #181c1f;
  color: #e6e6e6;
}
body.dark h1, body.dark h2, body.dark h3, body.dark h4 {
  color: #7ab7ff;
}
body.dark pre, body.dark code {
  background: #23272b;
  color: #e6e6e6;
}
body.dark blockquote {
  background: #23272b;
  color: #b0b0b0;
  border-left: 4px solid #7ab7ff;
}
.toggle-dark {
  position: fixed;
  top: 1.5em;
  right: 2em;
  background: #2a5d9f;
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 0.5em 1.2em;
  font-size: 1em;
  cursor: pointer;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: background 0.2s;
}
.toggle-dark:hover {
  background: #17406a;
}
@media (max-width: 600px) {
  body { padding: 0.5em; font-size: 1em; }
  .toggle-dark { top: 0.5em; right: 0.5em; }
}
</style>'''
    js = '''<script>
const btn = document.createElement('button');
btn.textContent = '🌙 Modo Escuro';
btn.className = 'toggle-dark';
document.addEventListener('DOMContentLoaded', () => {
  document.body.appendChild(btn);
  btn.onclick = () => {
    document.body.classList.toggle('dark');
    btn.textContent = document.body.classList.contains('dark') ? '☀️ Modo Claro' : '🌙 Modo Escuro';
  };
});
</script>'''
    page_title = title or md_path.stem
    html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{page_title}</title>{css}</head><body>{html_content}{js}</body></html>'
    html_path = md_path.with_suffix('.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return html_path

def create_html_directly(md_content: str, title: str, output_dir: Path) -> Path:
    """Cria um arquivo HTML diretamente do conteúdo markdown, sem arquivo intermediário."""
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'fenced_code', 'tables', 'toc', 'codehilite', 'sane_lists', 'smarty'
        ]
    )
    # CSS moderno com dark mode toggle
    css = '''<style>
body {
  max-width: 800px;
  margin: 2em auto;
  font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  background: #f9f9f9;
  color: #222;
  padding: 2em;
  line-height: 1.7;
  font-size: 1.1em;
  transition: background 0.3s, color 0.3s;
}
h1, h2, h3, h4 {
  color: #2a5d9f;
  margin-top: 2em;
}
pre, code {
  background: #eee;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Mono', 'Consolas', monospace;
  font-size: 1em;
}
pre {
  padding: 1em;
  overflow-x: auto;
}
blockquote {
  border-left: 4px solid #2a5d9f;
  padding-left: 1em;
  color: #555;
  background: #f3f7fa;
}
hr {
  border: 0;
  border-top: 1px solid #ccc;
  margin: 2em 0;
}
a {
  color: #2a5d9f;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
ul, ol {
  margin-left: 2em;
}
li {
  margin-bottom: 0.5em;
}
/* Dark mode */
body.dark {
  background: #181c1f;
  color: #e6e6e6;
}
body.dark h1, body.dark h2, body.dark h3, body.dark h4 {
  color: #7ab7ff;
}
body.dark pre, body.dark code {
  background: #23272b;
  color: #e6e6e6;
}
body.dark blockquote {
  background: #23272b;
  color: #b0b0b0;
  border-left: 4px solid #7ab7ff;
}
.toggle-dark {
  position: fixed;
  top: 1.5em;
  right: 2em;
  background: #2a5d9f;
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 0.5em 1.2em;
  font-size: 1em;
  cursor: pointer;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: background 0.2s;
}
.toggle-dark:hover {
  background: #17406a;
}
@media (max-width: 600px) {
  body { padding: 0.5em; font-size: 1em; }
  .toggle-dark { top: 0.5em; right: 0.5em; }
}
</style>'''
    js = '''<script>
const btn = document.createElement('button');
btn.textContent = '🌙 Modo Escuro';
btn.className = 'toggle-dark';
document.addEventListener('DOMContentLoaded', () => {
  document.body.appendChild(btn);
  btn.onclick = () => {
    document.body.classList.toggle('dark');
    btn.textContent = document.body.classList.contains('dark') ? '☀️ Modo Claro' : '🌙 Modo Escuro';
  };
});
</script>'''
    page_title = title or "Resumo"
    html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{page_title}</title>{css}</head><body>{html_content}{js}</body></html>'
    html_path = output_dir / f'{title}.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return html_path
