import os, collections
from datetime import datetime
import markdown

cwd = os.getcwd()
template_dir = os.path.join(cwd, 'templates')
source_dir = os.path.join(cwd, 'source')
post_dir = os.path.join(cwd, 'posts')

class Templates:
    def __init__(self, templ_dir):
        self.templates = {}
        files = [os.path.join(templ_dir, f) for f in os.listdir(templ_dir)]
        for fil in files:
            fn = os.path.basename(fil)
            with open(fil, 'r') as f:
                self.templates[fn] = f.read()
    def get(self, key):
        return self.templates[f'{key}.html']
    def __str__(self):
        ret = ''
        for k, v in self.templates.items():
            ret += f'{k}:\n{v}\n\n'
        return ret

templates = Templates(template_dir)


# Read sources and generate posts
index = []
files = [os.path.join(source_dir, f) for f in os.listdir(source_dir)]
files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
for fil in files:
    edited = datetime.utcfromtimestamp(os.path.getmtime(fil))
    fn = os.path.basename(fil).replace('.md', '') 
    fn_html = f'{fn}.html'

    with open(fil, 'r') as inf:
        text = inf.read()
        html = markdown.markdown(text, extensions=['fenced_code'])
        post_path = os.path.join(post_dir, fn_html)
        with open(post_path, "w") as of:
            of.write(''.join([templates.get('header-post').replace('[title]', fn), html, templates.get('footer-post')]))
        print(f'Wrote {fn_html} | updated {edited}')
        index.append({
            'title': fn,
            'path': post_path.replace(cwd, '.'),
            'edited': str(edited),
        })


# Generate index page
index_html = templates.get('header')
for item in index:
    row = templates.get('row').replace('[path]', item['path']).replace('[title]', item['title']).replace('[edited]', item['edited'])
    index_html += row
index_html += templates.get('footer')

with open('index.html', 'w') as f:
    f.write(index_html)
