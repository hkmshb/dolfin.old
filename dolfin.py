# -*- coding: utf-8 -*-
"""
A collection of general purpose utility functions and classes that can be used
within scripts and web applications.

Copyright (c) 2014, Hazeltek Solutions.
"""

__author__  = 'Hazeltek Solutions'
__version__ = '0.1'


import os, sys



def include_revision(func):
    """A decorator method which returns a function for extracting the latest 
    source control revision hash (and id if available) of a repository.
    """  

    def exec_command(cmd, **kwargs):
        """Executes a shell command with arguments in 'cmd' and returns the
        output as a byte string.
        """
        import shlex, subprocess
        try:
            args = shlex.split(cmd, None)
            out = subprocess.check_output(args)
            return out.strip()
        except:
            return None
    
    # defines command for extracting hash for different scc
    extractr_for = {
        '.hg': lambda: exec_command('hg.exe identify -i'),
        '.git': lambda: exec_command('git.exe')
    }

    def extract_revision(working_dir):
        # determine scc in use: hg or git
        extractr_key = None
        for key in extractr_for.keys():
            target_dir = os.path.join(working_dir, key)
            if os.path.exists(target_dir):
                extractr_key = key
                break

        if (not os.path.isdir(working_dir) and
            not working_dir.endswith('.egg') and 
            not working_dir.endswith('.whl')):
            raise ValueError('Invalid path provided. Path to a repository '
                             'directory or python .egg or .whl file expected')

        cwd_cache = os.getcwd()     # cache working directory
        if cwd_cache.lower() != working_dir.lower():
            os.chdir(working_dir)

        revision = extractr_for.get(extractr_key, lambda: None)()
        if not revision:
            # try reading [.]REVISION file if it exists
            for name in ('REVISION', '.REVISION'):
                filepath = os.path.join(working_dir, name)
                if os.path.isfile(filepath):
                    revision = open(filepath, 'r').readline()
        elif revision == b'000000000000':
            revision = None
        
        os.chdir(cwd_cache)         # restore working directory
        return revision

    def f(*args, **kwargs):
        version = func()
        if type(version) in (list, tuple):
            if len(version) < 3:
                version = list(version) + [0]
            elif len(version) > 3:
                version = version[:3]
            version = '.'.join([str(x) for x in version])

        # get scc revision number
        working_dir = (kwargs or {}).get('working_dir')
        if working_dir:
            del kwargs['working_dir']
        else:
            # use module to resolve working directory
            module_path = sys.modules[func.__module__].__path__[0]
            working_dir = os.path.abspath(os.path.join(module_path, '..'))

        revision = extract_revision(working_dir)
        if not revision:
            return version
        return '%s+%s' % (version, revision.decode())

    f.__doc__ = func.__doc__
    f.__name__ = func.__name__
    f.__module__ = func.__module__
    f.__dict__.update(func.__dict__)    
    return f
