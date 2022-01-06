import argparse, glob, json, os, re, socket, subprocess, shutil, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

HOST = 'localhost'
PORT = 8000
TEMPLATE = 'base.html'
TEMP = '.tmp'

class colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    LIGHT_GRAY = '\033[37m'
    GREEN = '\033[32m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class dynamicHandler(SimpleHTTPRequestHandler):
    '''
    Handler for the dynamic server option

    Render and serve page on request
    '''

    def set_header(self, response, keyword, value):
        self.send_response(response)
        self.send_header(keyword, value)
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            try:
                self.set_header(301, 'Location', '/' + sorted(glob.glob('[0-9][0-9][0-9][147]'), reverse=True)[0]), 
            except:
                self.set_header(404, "content-type", "text/html")
                self.wfile.write(bytes(load('<h1>No semester directories found</h1>\n', 'Page not found'), 'utf8'))
        elif os.path.isdir(self.path[1:]):
            content = contents(self.path)
            self.set_header(200, "content-type", "text/html")
            self.wfile.write(bytes(content, 'utf8'))
        elif os.path.isfile(self.path[1:] + '.md'):
            content = compile(self.path)
            self.set_header(200, "content-type", "text/html")
            self.wfile.write(bytes(content, 'utf8'))
        elif self.path.endswith('.pdf') and os.path.isfile(os.path.splitext(self.path)[0][1:] + '.md'):
            self.set_header(200, "content-type", "application/pdf")
            try:
                os.system(f'pandoc metadata.yaml {os.path.splitext(self.path)[0][1:]}.md -o {self.path[1:]}')
                self.wfile.write(open(self.path[1:], 'rb').read())
                os.remove(self.path[1:])
            except:
                warning('Unable to generate file')
        elif self.path.endswith('.png') and os.path.isfile(self.path[1:]):
            self.set_header(200, 'Content-type', 'image/png')
            self.wfile.write(open(self.path[1:], 'rb').read())
        else:
            self.set_header(404, "content-type", "text/html")
            self.wfile.write(bytes(load('<h1>Page not found</h1>\n', 'Page not found'), 'utf8'))
        
    def log_message(self, format, *args):
        return

class staticHandler(SimpleHTTPRequestHandler):
    '''
    Handler for the static server option

    Serve html files in specified directories
    '''

    def set_header(self, response, keyword, value):
        self.send_response(response)
        self.send_header(keyword, value)
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            try:
                self.set_header(301, 'Location', '/' + sorted(glob.glob('[0-9][0-9][0-9][147]'), reverse=True)[0]), 
            except:
                self.set_header(404, "content-type", "text/html")
                self.wfile.write(bytes(load('<h1>No semester directories found</h1>\n', 'Page not found'), 'utf8'))
        elif self.path.endswith('.png') and os.path.isfile(self.path[1:]):
            self.set_header(200, 'Content-type', 'image/png')
            self.wfile.write(open(self.path[1:], 'rb').read())
        elif self.path.endswith('.pdf') and os.path.isfile(os.path.splitext(self.path)[0][1:] + '.md'):
            self.set_header(200, "content-type", "application/pdf")
            try:
                os.system(f'pandoc metadata.yaml {os.path.splitext(self.path)[0][1:]}.md -o {self.path[1:]}')
                self.wfile.write(open(self.path[1:], 'rb').read())
                os.remove(self.path[1:])
            except:
                warning('Unable to generate file')
        else:
            self.path = f'{TEMP}{self.path}.html'
            if os.path.isfile(self.path):
                self.set_header(200, "content-type", "text/html")
                self.wfile.write(bytes(open(self.path, 'r').read(), 'utf8'))
            else:
                self.set_header(404, "content-type", "text/html")
                self.wfile.write(bytes(load('<h1>Page not found</h1>\n', 'Page not found'), 'utf8'))

    def log_message(self, format, *args):
        return

def load(content, title):
    '''
    Wrap HTML code in the template

    Parameters:
    content (str): HTML code of the content
    title (str): title of the page

    Returns:
    html (str): HTML code after the template is applied
    '''

    if not os.path.isfile(f'{TEMPLATE}'):
        error(f'Template file not found')

    with open(f'{TEMPLATE}') as _:
        base = _.read()
        base = re.sub(r'%title%', title, base)
        base = re.split(r'%content%', base)

    html = f'{base[0]}<div class="flex-wrapper">\n<div class="flex-sidebar">\n{navigation()}</div>\n<div class="flex-content">\n<div class="content">\n{content}</div>\n</div>\n</div>{base[1]}'

    return html

def compile(path):
    '''
    Convert the given markdown file into a web page

    Assumes that path is valid

    Parameters:
    path (str): The path of the markdown file

    Returns:
    (str): HTML code of the markdown file
    '''

    parts = os.path.splitext(path)[0].split('/')
    semester = parts[1]
    course = parts[2]
    basename = parts[3]

    with open(f'{semester}/{course}/{basename}.md') as _:
        title_match = re.findall('^#\s+([a-zA-Z0-9 ]*)\s*\n', _.read())
        if title_match:
            title = title_match[0]
        else:
            title = basename[2:].replace('-', ' ').title()
    
    content = subprocess.run(['pandoc', '--katex', f'{semester}/{course}/{basename}.md', '-t', 'html', '--output=-'], stdout=subprocess.PIPE, text=True).stdout

    return load(content, title)

def compileall():
    '''
    Compile all the markdown files into html files and places it in the temporary directory

    Parameters:
    None

    Return:
    None
    '''

    paths = []
    semesters = []

    for semester in next(os.walk('.'))[1]:
        if semester.isnumeric and len(semester) == 4 and semester[3] in ['1','4','7']:
            semesters.append(semester)
    for semester in semesters:
        for course in next(os.walk(f'{semester}'))[1]:
            files = glob.glob(f'{semester}/{course}/*.md')
            if files:
                for file in files:
                    paths.append(file)
        if not os.path.isdir(f'{TEMP}/{semester}'):
            os.makedirs(f'{TEMP}/{semester}')
        with open(f'{TEMP}/{semester}.html', 'w') as _:
            _.write(contents(f'{TEMP}/{semester}'))
            _.close()

    for path in paths:
        output = os.path.basename(os.path.splitext(path)[0])
        output_dir = f'{TEMP}/{os.path.dirname(path)}'
        with open(path, 'r') as _:
            title_match = re.findall('^#\s+([a-zA-Z0-9 ]*)\s*\n', _.read())
            if title_match:
                title = title_match[0]
            else:
                title = os.path.basename(output)[2:].replace('-', ' ').title()
            _.close()
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        with open(f'{output_dir}/{output}.html', 'w') as _:
            _.write(load(subprocess.run(['pandoc', '--katex', path, '-t', 'html', '--output=-'], stdout=subprocess.PIPE, text=True).stdout, title))

def contents(path):
    '''
    Generate a table of contents page for a given semester

    Assumes that path is valid

    Parameters:
    path (str): The path of the semester directory

    Returns:
    (str): HTML code of the table of contents page
    '''
    
    parts = os.path.splitext(path)[0].split('/')
    semester = parts[1]

    metadata = None
    
    try:
        with open('courses.json') as _:
            for entry in json.load(_):
                if str(entry['semester']) == semester:
                    metadata = entry
            _.close()
    except:
        warning('No metadata file found')

    content = f'# {semstring(int(semester))}'

    for course in sorted(next(os.walk(semester))[1]):
        if metadata:
            exists = False
            for course_entry in metadata['courses']:
                if course_entry['course'] == course:
                    exists = True
                    name = course_entry['name']
                    instructor = course_entry['instructor']
                    links = ''
                    for website in course_entry['websites']:
                        if website == course_entry['websites'][0]:
                            links += '('
                        site = website['name']
                        link = website['link']
                        links += f'[{site}]({link})'
                        if website != course_entry['websites'][-1]:
                            links += ', '
                        else:
                            links += ')'
            if exists:
                content += f'\n\n### {name}'
                content += f'\n\n{course.upper()[0:4]} {course[4:]}, {instructor}'
                if links:
                    content += f' {links}'
            else:
                name = course.upper()[0:4] + ' ' + course[4:]
                content += f'\n\n### {name}'
        else:
            name = course.upper()[0:4] + ' ' + course[4:]
            content += f'\n\n### {name}'
        content += '\n\n'
        for file in sorted(glob.glob(f'{semester}/{course}/*.md')):
            basename = os.path.splitext(os.path.basename(file))[0]
            number = basename[0]
            with open(file) as _:
                title = re.findall('^#\s+(.*)\s*(?:\n|$)', _.read())
                if title:
                    text = title[0]
                else:
                    text = basename[2:].replace('-', ' ').title()
            content += f'{number}. [{text}]({semester}/{course}/{basename}) &nbsp;[<i class="far fa-file-pdf"></i>]({semester}/{course}/{basename}.pdf)\n'

    content = subprocess.run(['pandoc', '-', '-f', 'markdown', '-t', 'html', '--output=-'], stdout=subprocess.PIPE, input=content, text=True).stdout
    
    return load(content, semstring(int(semester)))
    
def navigation():
    '''
    Generate the navigation bar

    Parameters:
    None

    Returns:
    content (str): HTML code of the navigation bar
    '''

    content = '<div class="sidebar">\n<span class="sidebar-title">Courses</span>\n<ul>\n'

    for semester in sorted(glob.glob('[0-9][0-9][0-9][147]'), reverse=True):
        content += f'<li class="sidebar-entry"><a href="/{semester}">{semstring(int(semester))}</a></li>\n'
    
    content += '</ul>\n</div>\n'

    return content

def semstring(semester):
    '''
    Convert a semester code to a string

    Parameters:
    semester (int): Semester code to be converted

    Return:
    semester_str (str): Converted string of the semester code
    '''
    
    if semester % 10 == 1:
        semester_str = 'Spring'
    elif semester % 10 == 4:
        semester_str = 'Summer'
    elif semester % 10 == 7:
        semester_str = 'Fall'

    semester_str += ' ' + str(19 + (semester // 10 ** 3)) + str((semester // 10) - (semester // 1000 * 100))

    return semester_str

def warning(message):
    '''
    Print a warning message

    Parameters:
    message (str): The warning message to be printed

    Return:
    None
    '''

    print(f'[{colors.BOLD}{colors.YELLOW}WARNING{colors.RESET}] {message}', file=sys.stderr)

def error(message):
    '''
    Print an error message and exit the program

    Parameters:
    message (str): The error message to be printed

    Return:
    None
    '''
    
    sys.exit(f'{os.path.basename(__file__)}: [{colors.BOLD}{colors.RED}ERROR{colors.RESET}]: {message}')

def clean():
    '''
    Clean temporary files that were created during runtime

    Parameters:
    None

    Return:
    None
    '''

    if os.path.isdir(TEMP):
        shutil.rmtree(TEMP)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--static', action='store_true', help='run the server in static mode')
    parser.add_argument('-p', '--port', type=int, default=8000, help='specify server port number')
    args = parser.parse_args()

    if args.port >= 1024:
        PORT = args.port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not sock.connect_ex((HOST, PORT)):
            sock.close()
            error(f'Port {PORT} is not available')
        sock.close()
    else:
        error('Invalid port number')

    if args.static:
        print('Generating HTML files...')
        compileall()

    with HTTPServer(('', PORT), staticHandler if args.static else dynamicHandler) as httpd:
        try:
            print(f'{colors.BOLD}{"Static" if args.static else "Dynamic"}{colors.RESET} server is running at {colors.UNDERLINE}{colors.GREEN}http://{HOST}:{PORT}{colors.RESET}')
            httpd.serve_forever()
        except:
            print(f'\r{colors.BOLD}{colors.RED}Shutting down server{colors.RESET}')
            httpd.shutdown()

    clean()

if __name__ == "__main__":
    main()
