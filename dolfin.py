# -*- coding: utf-8 -*-
"""
A collection of general purpose utility functions and classes that can be used
within scripts and web applications.

Copyright (c) 2014, Hazeltek Solutions.
"""

__author__  = 'Hazeltek Solutions'
__version__ = '0.1'


import os, sys
import json

from abc import ABCMeta, abstractmethod



class DolfinError(Exception):
    """Represents the base exception class for the library."""
    pass


class CommandError(DolfinError):
    """The exception thrown for a command related error."""
    pass


class ConfigNotFound(DolfinError):
    """The exception thrown when the configuration file is not found."""
    pass


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
        '.git': lambda: exec_command('git.exe rev-list HEAD -1')
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
        return '%s+%s' % (version, revision[:12].decode())

    f.__doc__ = func.__doc__
    f.__name__ = func.__name__
    f.__module__ = func.__module__
    f.__dict__.update(func.__dict__)    
    return f


class Command(object):
    """Represents the base class for Command objects."""
    __metaclass__ = ABCMeta

    def _execute(self, args):
        """Tries to execute this command; if it raises a CommandError, intercept
        it and print it sensibly to stderr.
        """
        try:
            output = self._handle(args)
            if output: print(output)
        except CommandError as ex:
            sys.stderr.write('Error: %s\n\n' % str(ex))
            sys.exit(1)
    
    def print_help(self, prog):
        """Prints the help message for this command."""
        p = self.create_parser(prog)
        p.print_help()
        print('')

    def run_from_argv(self, argv=None):
        """Handles default options then runs this command."""
        print('')
        argv = (sys.argv[1:] if argv is None else argv)
        p = self._create_parser()
        args = p.parse_args(argv)

        self._handle_default_args(args)
        self._execute(args)
    
    def _handle_default_args(self, args):
        if hasattr(args, 'pythonpath'):
            sys.path.insert(0, args.pythonpath)

    @abstractmethod
    def _create_parser(self):
        """Creates and returns the ArgumentParser which will be used to parse
        the arguments passed to this command. Must be overridden by subclasses.
        """
        pass
    
    @abstractmethod
    def _handle(self, args):
        """Performs the actual operation of the command. Must be overridden
        by subclasses.
        """
        pass


class SubCommand(object):
    """Represents the base class for a SubCommand object."""
    __metaclass__ = ABCMeta

    def __init__(self, parent):
        self._subparser = parent.create_subparser(self)
        self._parent = parent
    
    def _error(self, message):
        self._subparser.error(message)

    @abstractmethod
    def __call__(self, args):
        pass


class Storage(dict):
    """Represents a dictionary object whose elements can be accessed and set 
    using the dot object notation. Thus in addition to `foo['bar']`, `foo.bar` 
    can equally be used.
    """
    
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, key):
        return self.__getitem__(key)
    
    def __setattr__(self, key, value):
        self[key] = value

    def __getitem__(self, key):
        return dict.get(self, key, None)
    
    def __getstate__(self):
        return dict(self)

    def __setstate__(self, value):
        dict.__init__(self, value)

    def __repr__(self):
        return '<Storage %s>' % dict.__repr__(self)
    
    @staticmethod
    def make(obj):
        """Converts all dict-like elements of a dict or storage object into
        storage objects.
        """
        if not isinstance(obj, (dict,)):
            raise ValueError('obj must be a dict or dict-like object')
        
        _make = lambda d: Storage({ k: d[k] 
            if not isinstance(d[k], (dict, Storage))
            else _make(d[k])
                for k in d.keys()
        })
        return _make(obj)


class Config(Storage):
    """A dictionary which contains configuration settings."""

    class Meta(type):
        """Meta class for creating Config object types."""

        def __new__(cls, name, bases, attrs):
            _cls = type.__new__(cls, name, bases, attrs)
            _cls._func_defaults = Storage()
            _cls._defaults = Storage()
            return _cls
        
        def register_defaults(cls, **defaults):
            """Registers default configurations."""
            cls._defaults.update(Storage.make(defaults))

        def register_func_default(cls, key, function):
            """Registers a default function for a given key."""
            cls._func_defaults[key] = function
    

    __metaclass__ = Meta
    
    def __init__(self, filepath=None, **config):
        p = os.path
        config.update(meta=Storage(name=None, path=None))
        if filepath:            
            if not p.exists(filepath):
                relpath = p.relpath(p.dirname(filepath), os.getcwd())
                basename = p.basename(filepath)
                msg = '%s was not found in %s'                
                
                if relpath == '.':
                    raise ConfigNotFound(msg % (basename, 'current directory'))
                raise ConfigNotFound(msg % (basename, relpath))

            with open(filepath) as f:
                _config = Storage(json.load(f)) or Storage()

            _config.update(config)
            _config.meta = Storage(
                name = p.basename(filepath),
                path = p.dirname(filepath),
            )
            config = _config

        Storage.__init__(self, Storage.make(config))

    def __getitem__(self, key):
        if key not in self:
            if key in self._defaults:
                self[key] = self._defaults[key]
            elif key in self._func_defaults:
                self[key] = self._func_defaults[key](self, key)
        return dict.get(self, key, None)
    
    def __delitem__(self, key):
        if key not in self:
            return # fail silently
        return dict.__delitem__(self, key)

