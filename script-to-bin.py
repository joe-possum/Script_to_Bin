import sys
import getopt
import os

def exit_help(msg=None) :
    if None != msg :
        print('Error: %s'%(msg))
    print("Usage: script_to_bin [ options ] source [ source2 [ ... ] ] ] dest")
    print("  Options:\n    -h / --help\n    -v / --version")
    print("  Install python script[s] (.py) into dest\n  as executable[s] including version information")
    quit()
    
opts,params = getopt.getopt(sys.argv[1:],'hv',['help','version'])
for opt,param in opts :
    if '-h' == opt or '--help' == opt :
        exit_help()
    if '-v' == opt or '--version' == opt :
        print(s2b_get_version())
        quit()

if len(params) < 2 :
    exit_help('Missing source and dest')

dest = params[-1]
sources = params[:-1]

def read_git() :
    fh = os.popen('git log | grep Date','r')
    text = fh.read()
    fh.close()
    lines = text.split('\n')
    date = lines[0]
    fh = open('.git/config','r')
    text = fh.read()
    fh.close()
    lines = text.split('\n')
    for line in lines :
        tokens = line.split("url = ")
        if 2 == len(tokens) :
            url = tokens[1]
    return date,url

cwd = os.getcwd()
for psource in sources :
    path = os.path.dirname(psource)
    if '' != path :
        os.chdir(path)
    source = os.path.basename(psource)
    if len(source) < 3 :
        exit_help("can't determine type of ';%s'"%(source))
    date,url = read_git()
    extension = source[-3:]
    executable = source[:-3].split('/')[-1]
    if '.py' == extension :
        header = """#! /bin/env python3
# Installed by script-to-bin
# Repo:   %s
# %s
""" % (url,date)
        print(executable, date,url)
        fh = open(source,'r')
        text = fh.read()
        fh.close()
        lines = text.split('\n')
        got_sys = False
        got_getopt = False
        first_import = None
        counter = 0
        for line in lines :
            tokens = line.split()
            if len(tokens) > 1 :
                if 'import' == tokens[0] :
                    if None == first_import :
                        first_import = counter
                    last_import = counter
                    if 'sys' == tokens[1] :
                        got_sys = True
                    if 'getopt' == tokens[1] :
                        got_getopt = True
            counter += 1
        out = header + '\n'
        for i in range(first_import) :
            out += lines[i] + '\n'
        if not got_sys and not got_getopt :
            out += 'import sys\n'
        for i in range(first_import, last_import+1) :
            out += lines[i] + '\n'
        out += """
def s2b_get_version() :
    fh = open(sys.argv[0],'r')
    text = fh.read()
    fh.close()
    lines = text.split('\\n')
    if '# Installed by script-to-bin' == lines[1] :
        return lines[2][2:]+'\\n'+lines[3][2:]
    return "This can't happen!"
"""
        if not got_getopt :
            out += """
if len(sys.argv) > 1 :
    if '-v' == sys.argv[1] or '--version' == sys.argv[1] :
        print(s2b_get_version())
        quit()
"""
        for i in range(last_import+1,counter) :
            out += lines[i] + '\n'
        path = dest + '/' + executable
        fh = open(path,'w')
        fh.write(out)
        fh.close()
        os.chmod(path,int("0700",8))
    os.chdir(cwd)
