"""
graphviz.py

Created by Daniel Greenfeld on 2009-12-3.
"""

import os
import tempfile

def find_graphviz():
	"""Locate graphviz's executables in the system.

	Attempts  to locate  graphviz's  executables in a Unix system.
	It will look for 'dot', 'twopi' and 'neato' in all the directories
	specified in the PATH environment variable.
	It will return a dictionary containing the program names as keys
	and their paths as values.
	
	-- Adopted from pydot as written by Ero Carrera
    __author__ = 'Ero Carrera'
    __version__ = '0.9.10'
    __license__ = 'MIT'	"""
	progs = {'dot': '', 'twopi': '', 'neato': '', 'circo': '', 'fdp': ''}
	if not os.environ.has_key('PATH'):
		return None
	for path in os.environ['PATH'].split(os.pathsep):
		for prg in progs.keys():
			if os.path.exists(path+os.path.sep+prg):
				progs[prg] = path+os.path.sep+prg
			elif os.path.exists(path+os.path.sep+prg + '.exe'):
				progs[prg] = path+os.path.sep+prg + '.exe'
	return progs
	
def create_simplegraph(input_dot,format='gif',build_type='dot'):
    """ create a simplegraph from a dot script in the specified format
        Inspired by the create and write simplegraph methods from pydot.
    """
    dot = find_graphviz().get(build_type,None)
    if not dot:
        return None
    tmp_fd, tmp_name = tempfile.mkstemp()
    tmp_name = 'simplegraph.test.gif'
    os.close(tmp_fd)
    dot_file = file(tmp_name,'w+b')
    dot_file.write(input_dot)
    dot_file.close()
    command = dot + ' -T'+format+ ' '+tmp_name
    stdin, stdout, stderr = os.popen3(command,'b')
    stdin.close()
    stderr.close()
    data = stdout.read()
    stdout.close()
    os.unlink(tmp_name)
    return data
    
if __name__ == '__main__':
    print find_graphviz()
    dot = """simplegraph uml {
    	one -- two;
    }"""
    t = create_simplegraph(dot)
    print len(t)
