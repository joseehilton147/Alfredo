from pathlib import Path
import markdown
import time

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

def create_html_directly(md_content: str, title: str, output_dir: Path, output_filename: str = None) -> Path:
    """Cria um arquivo HTML moderno com Tailwind v4, sem sidebar e com funcionalidades de compartilhamento."""
    
    # Processar markdown com extensões avançadas
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'fenced_code', 'tables', 'toc', 'codehilite', 'sane_lists', 'smarty', 'attr_list'
        ]
    )
    
    # Estrutura HTML moderna e "vendável" com Tailwind v4
    page_title = title or "Resumo Inteligente"
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Resumo inteligente gerado pelo Alfredo AI">
    <meta name="generator" content="Alfredo AI">
    <title>{page_title}</title>
    
    <!-- Tailwind CSS v4 CDN -->
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <!-- Custom Styles -->
    <style type="text/tailwindcss">
        @theme {{
            --font-family-sans: 'Inter', system-ui, sans-serif;
            --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;
            
            --color-primary-50: #eff6ff;
            --color-primary-100: #dbeafe;
            --color-primary-500: #3b82f6;
            --color-primary-600: #2563eb;
            --color-primary-700: #1d4ed8;
            --color-primary-900: #1e3a8a;
        }}
        
        /* Animações customizadas */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes float {{
            0%, 100% {{
                transform: translateY(0px);
            }}
            50% {{
                transform: translateY(-10px);
            }}
        }}
        
        .animate-fade-in-up {{
            animation: fadeInUp 0.6s ease-out forwards;
        }}
        
        .animate-float {{
            animation: float 3s ease-in-out infinite;
        }}
        
        /* Gradientes customizados */
        .gradient-hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .gradient-card {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        /* Estilos para conteúdo markdown */
        .content h1 {{
            @apply text-4xl font-bold text-gray-900 dark:text-white mb-6 leading-tight;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .content h2 {{
            @apply text-3xl font-semibold text-gray-800 dark:text-gray-100 mt-12 mb-4 pb-2 border-b-2 border-primary-500;
        }}
        
        .content h3 {{
            @apply text-2xl font-medium text-gray-700 dark:text-gray-200 mt-8 mb-3;
        }}
        
        .content h4 {{
            @apply text-xl font-medium text-gray-600 dark:text-gray-300 mt-6 mb-2;
        }}
        
        .content p {{
            @apply text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed;
        }}
        
        .content ul, .content ol {{
            @apply space-y-3 mb-6 ml-6;
        }}
        
        .content li {{
            @apply text-lg text-gray-700 dark:text-gray-300 leading-relaxed relative;
        }}
        
        .content ul li::before {{
            content: "▶";
            @apply text-primary-500 font-bold absolute -left-6 top-0;
        }}
        
        .content ol {{
            counter-reset: item;
        }}
        
        .content ol li {{
            counter-increment: item;
        }}
        
        .content ol li::before {{
            content: counter(item) ".";
            @apply text-primary-500 font-bold absolute -left-8 top-0;
        }}
        
        /* Destaque especial para itens importantes */
        .content li:has(strong) {{
            @apply bg-gradient-to-r from-primary-50 to-transparent dark:from-primary-900/20 dark:to-transparent p-4 rounded-lg border-l-4 border-primary-500 shadow-sm hover:shadow-md transition-all duration-300 transform hover:translate-x-2;
        }}
        
        .content blockquote {{
            @apply bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-l-4 border-primary-500 p-6 rounded-r-lg shadow-lg italic text-lg relative mb-6;
        }}
        
        .content blockquote::before {{
            content: """;
            @apply text-6xl text-primary-500 opacity-30 absolute -top-2 left-2;
        }}
        
        .content code {{
            @apply bg-gray-100 dark:bg-gray-800 text-primary-600 dark:text-primary-400 px-2 py-1 rounded font-mono text-sm font-medium;
        }}
        
        .content pre {{
            @apply bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-xl overflow-x-auto shadow-lg border border-gray-700 mb-6;
        }}
        
        .content pre code {{
            @apply bg-transparent text-gray-100 p-0;
        }}
        
        .content a {{
            @apply text-primary-600 dark:text-primary-400 font-medium hover:text-primary-700 dark:hover:text-primary-300 transition-colors duration-200 underline-offset-4 hover:underline;
        }}
        
        /* Botões personalizados */
        .btn-primary {{
            @apply bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium px-6 py-3 rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center gap-2;
        }}
        
        .btn-secondary {{
            @apply bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 font-medium px-6 py-3 rounded-lg shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center gap-2;
        }}
        
        .btn-success {{
            @apply bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-medium px-6 py-3 rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center gap-2;
        }}
    </style>
</head>
<body class="bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <!-- Progress Bar -->
    <div id="progressBar" class="fixed top-0 left-0 h-1 bg-gradient-to-r from-primary-500 to-primary-600 z-50 transition-all duration-300" style="width: 0%"></div>
    
    <!-- Header Hero -->
    <header class="gradient-hero text-white py-16 px-4">
        <div class="max-w-6xl mx-auto">
            <div class="flex flex-col lg:flex-row items-center justify-between gap-8">
                <!-- Logo e Branding -->
                <div class="text-center lg:text-left">
                    <div class="flex items-center justify-center lg:justify-start gap-3 mb-4">
                        <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center text-2xl animate-float">
                            🤖
                        </div>
                        <h1 class="text-3xl font-bold">Alfredo AI</h1>
                    </div>
                    <p class="text-xl text-white/90 mb-2">Resumo Inteligente Gerado</p>
                    <div class="flex items-center justify-center lg:justify-start gap-4 text-sm text-white/80">
                        <span class="flex items-center gap-1">
                            <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                            Processamento Instantâneo
                        </span>
                        <span class="flex items-center gap-1">
                            <span class="text-yellow-400">⚡</span>
                            100% Automático
                        </span>
                    </div>
                </div>
                
                <!-- Controles -->
                <div class="flex flex-wrap items-center gap-3">
                    <button 
                        onclick="shareContent()" 
                        class="btn-primary bg-white/20 hover:bg-white/30 backdrop-blur-sm">
                        <span class="text-xl">📤</span>
                        Compartilhar
                    </button>
                    <button 
                        onclick="window.print()" 
                        class="btn-secondary bg-white/10 hover:bg-white/20 backdrop-blur-sm border-white/30 text-white">
                        <span class="text-xl">🖨️</span>
                        Salvar PDF
                    </button>
                    <button 
                        onclick="toggleTheme()" 
                        id="themeToggle"
                        class="btn-secondary bg-white/10 hover:bg-white/20 backdrop-blur-sm border-white/30 text-white">
                        <span class="text-xl">🌙</span>
                        Modo Escuro
                    </button>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Main Content -->
    <main class="max-w-5xl mx-auto px-4 py-12">
        <!-- Título do Conteúdo -->
        <div class="text-center mb-12 animate-fade-in-up">
            <h2 class="text-4xl font-bold text-gray-900 dark:text-white mb-4">{page_title}</h2>
            <p class="text-xl text-gray-600 dark:text-gray-400">Gerado em {time.strftime('%d/%m/%Y às %H:%M')}</p>
        </div>
        
        <!-- Conteúdo Processado -->
        <article class="content bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 lg:p-12 animate-fade-in-up">
            {html_content}
        </article>
        
        <!-- CTA Section -->
        <section class="mt-16 text-center animate-fade-in-up">
            <div class="bg-gradient-to-r from-primary-500 to-purple-600 rounded-2xl p-8 text-white">
                <h3 class="text-3xl font-bold mb-4">🎯 Gostou do resultado?</h3>
                <p class="text-xl mb-6 text-white/90">Compartilhe este resumo inteligente com seus colegas e amigos!</p>
                
                <div class="flex flex-wrap justify-center gap-4">
                    <button onclick="shareWhatsApp()" class="btn-success bg-green-500 hover:bg-green-600">
                        <span class="text-xl">📱</span>
                        WhatsApp
                    </button>
                    <button onclick="shareEmail()" class="btn-secondary bg-white/20 hover:bg-white/30 border-white/30 text-white">
                        <span class="text-xl">📧</span>
                        Email
                    </button>
                    <button onclick="shareLinkedIn()" class="btn-primary bg-blue-600 hover:bg-blue-700">
                        <span class="text-xl">💼</span>
                        LinkedIn
                    </button>
                    <button onclick="copyLink()" class="btn-secondary bg-white/20 hover:bg-white/30 border-white/30 text-white">
                        <span class="text-xl">📋</span>
                        Copiar Link
                    </button>
                </div>
            </div>
        </section>
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12 px-4 mt-16">
        <div class="max-w-6xl mx-auto text-center">
            <div class="flex items-center justify-center gap-3 mb-4">
                <div class="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center text-xl">
                    🤖
                </div>
                <span class="text-2xl font-bold">Alfredo AI</span>
            </div>
            <p class="text-gray-400 mb-4">Processamento inteligente de conteúdo com IA de última geração</p>
            <div class="flex justify-center items-center gap-6 text-sm text-gray-500">
                <span>📝 Resumo gerado automaticamente</span>
                <span>•</span>
                <span>⚡ Processamento instantâneo</span>
                <span>•</span>
                <span>🎯 100% preciso</span>
            </div>
        </div>
    </footer>
    
    <!-- Notification Container -->
    <div id="notifications" class="fixed top-4 right-4 z-50 space-y-2"></div>
    
    <!-- JavaScript -->
    <script>
        // Theme Management
        function toggleTheme() {{
            const html = document.documentElement;
            const isDark = html.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            const btn = document.getElementById('themeToggle');
            btn.innerHTML = isDark 
                ? '<span class="text-xl">☀️</span> Modo Claro'
                : '<span class="text-xl">🌙</span> Modo Escuro';
        }}
        
        // Initialize theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        if (savedTheme === 'dark') {{
            document.documentElement.classList.add('dark');
            document.getElementById('themeToggle').innerHTML = '<span class="text-xl">☀️</span> Modo Claro';
        }}
        
        // Reading Progress
        window.addEventListener('scroll', () => {{
            const scrolled = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
            document.getElementById('progressBar').style.width = `${{Math.min(scrolled, 100)}}%`;
        }});
        
        // Sharing Functions
        async function shareContent() {{
            const title = document.title;
            const url = window.location.href;
            const text = `📝 Confira este resumo inteligente gerado pelo Alfredo AI: ${{title}}`;

            if (navigator.share) {{
                try {{
                    await navigator.share({{ title, text, url }});
                    showNotification('Compartilhado com sucesso! 🎉', 'success');
                }} catch (err) {{
                    if (err.name !== 'AbortError') {{
                        fallbackShare();
                    }}
                }}
            }} else {{
                fallbackShare();
            }}
        }}
        
        function fallbackShare() {{
            copyLink();
            showNotification('Link copiado! Use o botão de compartilhar específico abaixo 👇', 'info');
        }}
        
        async function copyLink() {{
            try {{
                await navigator.clipboard.writeText(window.location.href);
                showNotification('Link copiado! 📋', 'success');
            }} catch (err) {{
                showNotification('Erro ao copiar link', 'error');
            }}
        }}
        
        function shareWhatsApp() {{
            const text = encodeURIComponent(`📝 *${{document.title}}*\\n\\nConfira este resumo inteligente gerado pelo Alfredo AI!\\n\\n${{window.location.href}}\\n\\n🤖 _Processado com IA para sua conveniência_`);
            window.open(`https://wa.me/?text=${{text}}`, '_blank');
        }}
        
        function shareEmail() {{
            const title = encodeURIComponent(document.title);
            const body = encodeURIComponent(`Confira este resumo inteligente gerado pelo Alfredo AI:\\n\\n${{window.location.href}}\\n\\nProcessado com inteligência artificial para sua conveniência! 🤖`);
            window.open(`mailto:?subject=${{title}}&body=${{body}}`);
        }}
        
        function shareLinkedIn() {{
            const url = encodeURIComponent(window.location.href);
            const title = encodeURIComponent(document.title);
            const summary = encodeURIComponent('Resumo inteligente gerado pelo Alfredo AI - Processamento automático de conteúdo com inteligência artificial');
            window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${{url}}&title=${{title}}&summary=${{summary}}`, '_blank');
        }}
        
        // Notifications
        function showNotification(message, type = 'info') {{
            const notification = document.createElement('div');
            const colors = {{
                success: 'bg-green-500',
                error: 'bg-red-500',
                info: 'bg-blue-500',
                warning: 'bg-yellow-500'
            }};
            
            notification.className = `${{colors[type]}} text-white px-6 py-3 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300`;
            notification.textContent = message;
            
            document.getElementById('notifications').appendChild(notification);
            
            setTimeout(() => {{
                notification.style.transform = 'translateX(0)';
            }}, 100);
            
            setTimeout(() => {{
                notification.style.transform = 'translateX(full)';
                setTimeout(() => notification.remove(), 300);
            }}, 3000);
        }}
        
        // Animate elements on scroll
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('animate-fade-in-up');
                }}
            }});
        }}, {{ threshold: 0.1 }});

        document.querySelectorAll('.content > *').forEach(el => {{
            observer.observe(el);
        }});
        
        // Smooth scroll for anchor links
        document.addEventListener('click', (e) => {{
            if (e.target.matches('a[href^="#"]')) {{
                e.preventDefault();
                const target = document.querySelector(e.target.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    # Salvar o arquivo
    if output_filename is None:
        output_filename = f'{title}.html'
    html_path = output_dir / output_filename
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return html_path

    # CSS moderno com foco em acessibilidade e responsividade
    css = '''<style>
/* Reset e base styles */
:root {
  --primary-50: #eff6ff;
  --primary-100: #dbeafe;
  --primary-500: #3b82f6;
  --primary-600: #2563eb;
  --primary-700: #1d4ed8;
}

/* Design system unificado */
.gradient-hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Typography premium */
.prose-custom {
  @apply max-w-none;
}

.prose-custom h1 {
  @apply text-5xl font-bold text-gray-900 dark:text-gray-100 mb-6 leading-tight bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent;
}

.prose-custom h2 {
  @apply text-3xl font-semibold text-gray-800 dark:text-gray-100 mt-12 mb-4 pb-2 border-b-2 border-primary-500;
}

.prose-custom h3 {
  @apply text-2xl font-medium text-gray-700 dark:text-gray-200 mt-8 mb-3;
}

.prose-custom h4 {
  @apply text-xl font-medium text-gray-600 dark:text-gray-300 mt-6 mb-2;
}

.prose-custom p {
  @apply text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed;
}

.prose-custom ul, .prose-custom ol {
  @apply space-y-3 mb-6;
}

.prose-custom li {
  @apply text-lg text-gray-700 dark:text-gray-300 leading-relaxed pl-2 relative;
}

.prose-custom ul li::before {
  content: "▶";
  @apply text-primary-500 font-bold absolute -left-6 top-0;
}

.prose-custom ol {
  counter-reset: item;
}

.prose-custom ol li {
  counter-increment: item;
}

.prose-custom ol li::before {
  content: counter(item) ".";
  @apply text-primary-500 font-bold absolute -left-8 top-0;
}

/* Destaque especial para itens importantes */
.prose-custom li:has(strong) {
  @apply bg-gradient-to-r from-primary-50 to-transparent dark:from-primary-900/20 dark:to-transparent p-4 rounded-lg border-l-4 border-primary-500 shadow-sm hover:shadow-md transition-all duration-300 transform hover:translate-x-2;
}

.prose-custom blockquote {
  @apply bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-l-4 border-primary-500 p-6 rounded-r-lg shadow-lg italic text-lg relative;
}

.prose-custom blockquote::before {
  content: """;
  @apply text-6xl text-primary-500 opacity-30 absolute -top-2 left-2;
}

.prose-custom code {
  @apply bg-gray-100 dark:bg-gray-800 text-primary-600 dark:text-primary-400 px-2 py-1 rounded font-mono text-sm font-medium;
}

.prose-custom pre {
  @apply bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-xl overflow-x-auto shadow-lg border border-gray-700;
}

.prose-custom pre code {
  @apply bg-transparent text-gray-100 p-0;
}

.prose-custom a {
  @apply text-primary-600 dark:text-primary-400 font-medium hover:text-primary-700 dark:hover:text-primary-300 transition-colors duration-200 underline-offset-4 hover:underline;
}

/* Botões estilizados */
.btn-primary {
  @apply bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium px-6 py-3 rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center gap-2;
}

.btn-secondary {
  @apply bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 font-medium px-6 py-3 rounded-lg shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center gap-2;
}

.btn-success {
  @apply bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-medium px-6 py-3 rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center gap-2;
}

/* Cards e containers */
.card {
  @apply bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden;
}

.card-hover {
  @apply hover:shadow-2xl hover:scale-105 transition-all duration-300;
}

/* Responsividade aprimorada */
@media (max-width: 768px) {
  .prose-custom h1 {
    @apply text-3xl;
  }
  
  .prose-custom h2 {
    @apply text-2xl;
  }
  
  .prose-custom li:has(strong) {
    @apply hover:translate-x-1;
  }
}

/* Dark mode aprimorado */
.dark .gradient-hero {
  background: linear-gradient(135deg, #1e3a8a 0%, #312e81 100%);
}

/* Tooltip customizado */
.tooltip {
  @apply relative;
}

.tooltip::after {
  content: attr(data-tooltip);
  @apply absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-gray-900 text-white text-sm rounded-lg opacity-0 pointer-events-none transition-opacity duration-200;
}

.tooltip:hover::after {
  @apply opacity-100;
}
</style>'''
    
    # JavaScript moderno com funcionalidades de compartilhamento e interação
    js = '''<script>
class AlfredoViewer {
  constructor() {
    this.init();
  }

  init() {
    this.setupTheme();
    this.setupSharing();
    this.setupInteractions();
    this.setupAnalytics();
    this.addEnhancements();
  }

  setupTheme() {
    // Restaurar tema salvo
    const savedTheme = localStorage.getItem('alfredo-theme') || 'light';
    document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    
    // Event listener para toggle do tema
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-action="toggle-theme"]')) {
        this.toggleTheme();
      }
    });
  }

  toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('alfredo-theme', isDark ? 'dark' : 'light');
    
    // Atualizar ícone do botão
    const themeBtn = document.querySelector('[data-action="toggle-theme"]');
    if (themeBtn) {
      themeBtn.innerHTML = isDark 
        ? '<span class="text-xl">☀️</span> Modo Claro'
        : '<span class="text-xl">🌙</span> Modo Escuro';
    }
    
    // Animação suave
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
  }

  setupSharing() {
    // Compartilhar via Web Share API ou fallback
    document.addEventListener('click', async (e) => {
      if (e.target.matches('[data-action="share"]')) {
        await this.shareContent();
      }
      
      if (e.target.matches('[data-action="copy-link"]')) {
        await this.copyLink();
      }
      
      if (e.target.matches('[data-action="download-pdf"]')) {
        this.downloadPDF();
      }
      
      if (e.target.matches('[data-action="email"]')) {
        this.shareByEmail();
      }
      
      if (e.target.matches('[data-action="whatsapp"]')) {
        this.shareWhatsApp();
      }
      
      if (e.target.matches('[data-action="linkedin"]')) {
        this.shareLinkedIn();
      }
    });
  }

  async shareContent() {
    const title = document.title;
    const url = window.location.href;
    const text = `📝 Confira este resumo inteligente gerado pelo Alfredo AI: ${title}`;

    if (navigator.share) {
      try {
        await navigator.share({ title, text, url });
        this.showNotification('Compartilhado com sucesso! 🎉', 'success');
      } catch (err) {
        if (err.name !== 'AbortError') {
          this.fallbackShare();
        }
      }
    } else {
      this.fallbackShare();
    }
  }

  fallbackShare() {
    // Mostrar modal de compartilhamento
    this.showShareModal();
  }

  async copyLink() {
    try {
      await navigator.clipboard.writeText(window.location.href);
      this.showNotification('Link copiado! 📋', 'success');
    } catch (err) {
      this.showNotification('Erro ao copiar link', 'error');
    }
  }

  downloadPDF() {
    // Trigger print dialog (usuário pode salvar como PDF)
    this.showNotification('Abrindo diálogo de impressão... 🖨️', 'info');
    setTimeout(() => window.print(), 500);
  }

  shareByEmail() {
    const title = encodeURIComponent(document.title);
    const body = encodeURIComponent(`Confira este resumo inteligente gerado pelo Alfredo AI:\\n\\n${window.location.href}\\n\\nProcessado com inteligência artificial para sua conveniência! 🤖`);
    window.open(`mailto:?subject=${title}&body=${body}`);
  }

  shareWhatsApp() {
    const text = encodeURIComponent(`📝 *${document.title}*\\n\\nConfira este resumo inteligente gerado pelo Alfredo AI!\\n\\n${window.location.href}\\n\\n🤖 _Processado com IA para sua conveniência_`);
    window.open(`https://wa.me/?text=${text}`, '_blank');
  }

  shareLinkedIn() {
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent(document.title);
    const summary = encodeURIComponent('Resumo inteligente gerado pelo Alfredo AI - Processamento automático de conteúdo com inteligência artificial');
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}&title=${title}&summary=${summary}`, '_blank');
  }

  showShareModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4';
    modal.innerHTML = `
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full animate-slide-up">
        <div class="text-center mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">📤 Compartilhar Resumo</h3>
          <p class="text-gray-600 dark:text-gray-400">Escolha como deseja compartilhar este conteúdo</p>
        </div>
        
        <div class="grid grid-cols-2 gap-3 mb-6">
          <button data-action="whatsapp" class="btn-success">
            <span class="text-xl">📱</span> WhatsApp
          </button>
          <button data-action="email" class="btn-secondary">
            <span class="text-xl">📧</span> Email
          </button>
          <button data-action="linkedin" class="btn-primary">
            <span class="text-xl">💼</span> LinkedIn
          </button>
          <button data-action="copy-link" class="btn-secondary">
            <span class="text-xl">📋</span> Copiar Link
          </button>
        </div>
        
        <button class="w-full btn-secondary" onclick="this.closest('.fixed').remove()">
          Cancelar
        </button>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Fechar ao clicar fora
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  }

  setupInteractions() {
    // Smooth scroll para âncoras
    document.addEventListener('click', (e) => {
      if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });

    // Animações de entrada
    this.setupScrollAnimations();
    
    // Reading progress
    this.setupReadingProgress();
  }

  setupScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-slide-up');
        }
      });
    }, { threshold: 0.1 });

    // Observar elementos do conteúdo
    document.querySelectorAll('.prose-custom > *').forEach(el => {
      observer.observe(el);
    });
  }

  setupReadingProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'fixed top-0 left-0 h-1 bg-gradient-to-r from-primary-500 to-primary-600 z-50 transition-all duration-300';
    progressBar.style.width = '0%';
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
      const scrolled = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
      progressBar.style.width = \`\${Math.min(scrolled, 100)}%\`;
    });
  }

  setupAnalytics() {
    // Tracking de engagement
    this.trackTimeOnPage();
    this.trackScrollDepth();
  }

  trackTimeOnPage() {
    this.startTime = Date.now();
    
    window.addEventListener('beforeunload', () => {
      const timeSpent = Math.round((Date.now() - this.startTime) / 1000);
      console.log(`Tempo na página: ${timeSpent}s`);
    });
  }

  trackScrollDepth() {
    let maxScroll = 0;
    
    window.addEventListener('scroll', () => {
      const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
      maxScroll = Math.max(maxScroll, scrollPercent);
    });
  }

  addEnhancements() {
    // Adicionar tooltips
    this.addTooltips();
    
    // Adicionar copy code buttons
    this.addCodeCopyButtons();
    
    // Adicionar table of contents se necessário
    this.generateTOC();
    
    // Easter egg
    this.addEasterEgg();
  }

  addTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(el => {
      el.classList.add('tooltip');
    });
  }

  addCodeCopyButtons() {
    document.querySelectorAll('pre code').forEach(codeBlock => {
      const pre = codeBlock.parentElement;
      const button = document.createElement('button');
      button.className = 'absolute top-2 right-2 bg-gray-700 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors';
      button.innerHTML = '📋 Copiar';
      
      pre.style.position = 'relative';
      pre.appendChild(button);
      
      button.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(codeBlock.textContent);
          button.innerHTML = '✅ Copiado!';
          setTimeout(() => {
            button.innerHTML = '📋 Copiar';
          }, 2000);
        } catch (err) {
          button.innerHTML = '❌ Erro';
        }
      });
    });
  }

  generateTOC() {
    const headings = document.querySelectorAll('.prose-custom h1, .prose-custom h2, .prose-custom h3');
    if (headings.length < 3) return; // Só gerar TOC se houver suficientes headings

    const tocContainer = document.createElement('div');
    tocContainer.className = 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 mb-8 border border-blue-200 dark:border-blue-800';
    tocContainer.innerHTML = \`
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <span class="text-2xl">📋</span> Índice
      </h3>
      <ul class="space-y-2"></ul>
    \`;

    const tocList = tocContainer.querySelector('ul');
    
    headings.forEach((heading, index) => {
      if (!heading.id) {
        heading.id = \`heading-\${index}\`;
      }

      const li = document.createElement('li');
      li.innerHTML = \`
        <a href="#\${heading.id}" class="block text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors py-1 text-sm font-medium">
          \${heading.textContent}
        </a>
      \`;
      
      if (heading.tagName === 'H3') {
        li.style.marginLeft = '1rem';
        li.style.fontSize = '0.875rem';
      }
      
      tocList.appendChild(li);
    });

    // Inserir TOC após o primeiro parágrafo
    const firstP = document.querySelector('.prose-custom p');
    if (firstP) {
      firstP.after(tocContainer);
    }
  }

  addEasterEgg() {
    let clicks = 0;
    document.addEventListener('click', (e) => {
      if (e.target.matches('.footer-logo')) {
        clicks++;
        if (clicks === 5) {
          this.showNotification('🎉 Você descobriu o easter egg! Alfredo AI agradece! 🤖', 'success');
          clicks = 0;
        }
      }
    });
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const colors = {
      success: 'bg-green-500',
      error: 'bg-red-500',
      info: 'bg-blue-500',
      warning: 'bg-yellow-500'
    };
    
    notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Animate out
    setTimeout(() => {
      notification.style.transform = 'translateX(full)';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  new AlfredoViewer();
});

// Preload de fontes para performance
const fontPreload = document.createElement('link');
fontPreload.rel = 'preload';
fontPreload.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap';
fontPreload.as = 'style';
document.head.appendChild(fontPreload);
</script>'''
    
    # Processar o conteúdo markdown
    def process_content(content):
        """Processa o conteúdo para melhorar a estrutura HTML"""
        # Adicionar classes Tailwind para listas
        content = content.replace('<ul>', '<ul class="space-y-3">')
        content = content.replace('<ol>', '<ol class="space-y-3">')
        # Processar tabelas
        content = content.replace('<table>', '<table class="w-full border-collapse bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-lg">')
        return content
    
    processed_content = process_content(html_content)
    
    # Estrutura HTML moderna e vendável
    page_title = title or "Resumo Inteligente"
    html = f'''<!DOCTYPE html>
<html lang="pt-BR" class="scroll-smooth">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Resumo inteligente gerado pelo Alfredo AI - Processamento automático de conteúdo com IA">
    <meta name="keywords" content="resumo, inteligência artificial, IA, processamento de texto, Alfredo AI">
    <meta name="author" content="Alfredo AI">
    <meta name="generator" content="Alfredo AI v2.0">
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:title" content="{page_title}">
    <meta property="og:description" content="Resumo inteligente gerado pelo Alfredo AI">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{page_title}">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{page_title}">
    <meta name="twitter:description" content="Resumo inteligente gerado pelo Alfredo AI">
    
    <title>{page_title} | Alfredo AI</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <!-- Favicon -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
    
    {css}
</head>
<body class="bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <!-- Hero Section -->
    <header class="gradient-hero text-white">
        <div class="container mx-auto px-4 py-12">
            <div class="text-center max-w-4xl mx-auto">
                <div class="flex items-center justify-center gap-3 mb-6">
                    <div class="animate-float">
                        <span class="text-6xl">🤖</span>
                    </div>
                    <div>
                        <h1 class="text-4xl md:text-6xl font-bold mb-2">
                            Alfredo AI
                        </h1>
                        <p class="text-xl md:text-2xl opacity-90">
                            Resumo Inteligente Gerado
                        </p>
                    </div>
                </div>
                
                <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6 mb-8">
                    <h2 class="text-2xl md:text-3xl font-semibold mb-4 line-clamp-2">
                        {page_title}
                    </h2>
                    <div class="flex flex-wrap items-center justify-center gap-4 text-sm">
                        <span class="flex items-center gap-2">
                            <span class="text-lg">📅</span>
                            Gerado em {time.strftime('%d/%m/%Y às %H:%M')}
                        </span>
                        <span class="flex items-center gap-2">
                            <span class="text-lg">⚡</span>
                            Processamento Instantâneo
                        </span>
                        <span class="flex items-center gap-2">
                            <span class="text-lg">✨</span>
                            100% Automático
                        </span>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="flex flex-wrap items-center justify-center gap-4">
                    <button data-action="share" class="btn-primary animate-pulse-glow">
                        <span class="text-xl">📤</span>
                        Compartilhar
                    </button>
                    
                    <button data-action="download-pdf" class="btn-secondary">
                        <span class="text-xl">📄</span>
                        Salvar PDF
                    </button>
                    
                    <button data-action="toggle-theme" class="btn-secondary">
                        <span class="text-xl">🌙</span>
                        Modo Escuro
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Wave divider -->
        <div class="relative">
            <svg class="w-full h-20 text-gray-50 dark:text-gray-900" viewBox="0 0 1440 120" fill="currentColor">
                <path d="M0,64L48,69.3C96,75,192,85,288,90.7C384,96,480,96,576,85.3C672,75,768,53,864,48C960,43,1056,53,1152,64C1248,75,1344,85,1392,90.7L1440,96L1440,120L1392,120C1344,120,1248,120,1152,120C1056,120,960,120,864,120C768,120,672,120,576,120C480,120,384,120,288,120C192,120,96,120,48,120L0,120Z"></path>
            </svg>
        </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-12 max-w-4xl">
        <!-- Content Card -->
        <article class="card card-hover mb-12">
            <div class="p-8 md:p-12">
                <div class="prose-custom">
                    {processed_content}
                </div>
            </div>
        </article>

        <!-- CTA Section -->
        <section class="text-center mb-12">
            <div class="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-8 text-white">
                <h3 class="text-2xl md:text-3xl font-bold mb-4">
                    Gostou do resultado? 🎉
                </h3>
                <p class="text-lg mb-6 opacity-90">
                    Compartilhe este resumo inteligente com seus colegas e amigos!
                </p>
                
                <div class="flex flex-wrap items-center justify-center gap-4">
                    <button data-action="whatsapp" class="btn-success">
                        <span class="text-xl">📱</span>
                        WhatsApp
                    </button>
                    
                    <button data-action="linkedin" class="btn-primary">
                        <span class="text-xl">💼</span>
                        LinkedIn
                    </button>
                    
                    <button data-action="email" class="btn-secondary">
                        <span class="text-xl">📧</span>
                        Email
                    </button>
                    
                    <button data-action="copy-link" class="btn-secondary">
                        <span class="text-xl">📋</span>
                        Copiar Link
                    </button>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="grid md:grid-cols-3 gap-6 mb-12">
            <div class="card card-hover text-center p-6">
                <div class="text-4xl mb-4">⚡</div>
                <h4 class="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
                    Processamento Rápido
                </h4>
                <p class="text-gray-600 dark:text-gray-400">
                    IA avançada que processa conteúdo em segundos
                </p>
            </div>
            
            <div class="card card-hover text-center p-6">
                <div class="text-4xl mb-4">🎯</div>
                <h4 class="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
                    Resumos Precisos
                </h4>
                <p class="text-gray-600 dark:text-gray-400">
                    Extrai automaticamente os pontos mais importantes
                </p>
            </div>
            
            <div class="card card-hover text-center p-6">
                <div class="text-4xl mb-4">📱</div>
                <h4 class="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
                    Totalmente Responsivo
                </h4>
                <p class="text-gray-600 dark:text-gray-400">
                    Perfeito em qualquer dispositivo
                </p>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12">
        <div class="container mx-auto px-4 text-center">
            <div class="flex items-center justify-center gap-3 mb-6">
                <span class="text-4xl footer-logo cursor-pointer">🤖</span>
                <div>
                    <h5 class="text-2xl font-bold">Alfredo AI</h5>
                    <p class="text-gray-400">Inteligência Artificial a seu serviço</p>
                </div>
            </div>
            
            <div class="flex flex-wrap items-center justify-center gap-6 mb-6 text-sm">
                <span class="flex items-center gap-2">
                    <span class="text-green-400">✅</span>
                    Processamento 100% Automático
                </span>
                <span class="flex items-center gap-2">
                    <span class="text-blue-400">🚀</span>
                    Tecnologia de Ponta
                </span>
                <span class="flex items-center gap-2">
                    <span class="text-purple-400">🎯</span>
                    Resultados Precisos
                </span>
            </div>
            
            <div class="border-t border-gray-700 pt-6">
                <p class="text-gray-400 text-sm">
                    © 2025 Alfredo AI. Todos os direitos reservados. 
                    <br class="md:hidden">
                    Resumo gerado automaticamente com inteligência artificial.
                </p>
            </div>
        </div>
    </footer>

    {js}
</body>
</html>'''
    if output_filename is None:
        output_filename = f'{title}.html'
    html_path = output_dir / output_filename
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return html_path
