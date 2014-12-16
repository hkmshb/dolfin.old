"""
Defines unit tests for dolfin.
"""
import os, sys
import unittest

import dolfin



@dolfin.include_revision
def get_localver():
    return (0, 1)


class DolfinAttrTest(unittest.TestCase):
    ""    
    def test_author_isdefined(self):
        self.assertEqual('Hazeltek Solutions', dolfin.__author__)

    def test_version_isdefined(self):
        self.assertTrue(
            dolfin.__version__ != None and 
            dolfin.__version__.strip() != ''
        )


class RepositoryRevisionTest(unittest.TestCase):
    ""
    # target repo
    working_dir = os.path.join(os.path.dirname(__file__), r'data\test_repo')

    @classmethod
    def exec_script(cls, script_path):
        ""
        import shlex, subprocess

        cwd_cache = os.getcwd()     # cache cwd
        if cwd_cache.lower() != cls.working_dir.lower():
            os.chdir(cls.working_dir)

        cmdtext = 'powershell.exe -ExecutionPolicy Bypass ' + script_path
        args = shlex.split(cmdtext)
        subprocess.call(args)

        os.chdir(cwd_cache)         # restore cwd

    def test_non_repo_has_no_revision(self):
        ""
        _working_dir = os.environ.get('home', r'c:\\')
        version = get_localver(working_dir=_working_dir)
        self.assertEqual('0.1.0', version)
        self.assertFalse(version.startswith('0.1.0+'))


class HgRevisionTest(RepositoryRevisionTest):
    ""

    @classmethod
    def setUpClass(cls):
        ""
        cls.exec_script(r'.\\build-hg-repos.ps1')

    @classmethod
    def tearDownClass(cls):
        ""
        cls.exec_script(r'.\\clean-hg-repos.ps1')

    def test_blank_hg_repo_has_no_revision(self):
        ""
        _working_dir = os.path.join(self.working_dir, r'_ignore\\hg-repo1')
        version = get_localver(working_dir=_working_dir)
        self.assertEqual('0.1.0', version)
        self.assertFalse(version.startswith('0.1.0+'))

    def test_hg_repo_with_commit_has_revision(self):
        ""
        _working_dir = os.path.join(self.working_dir, r'_ignore\\hg-repo2')
        version = get_localver(working_dir=_working_dir)
        self.assertEqual('0.1.0+e7e5f581b991', version)


class GitRevisionTest(RepositoryRevisionTest):
    ""

    @classmethod
    def setUpClass(cls):
        ""
        cls.exec_script(r'.\\build-git-repos.ps1')

    @classmethod
    def tearDownClass(cls):
        ""
        cls.exec_script(r'.\\clean-git-repos.ps1')

    def test_blank_git_repo_has_no_revision(self):
        ""
        _working_dir = os.path.join(self.working_dir, r'_ignore\git-repo1')
        version = get_localver(working_dir=_working_dir)
        self.assertEqual('0.1.0', version)
        self.assertFalse(version.startswith('0.1.0+'))

    def test_git_repo_with_commit_has_revision(self):
        ""
        _working_dir = os.path.join(self.working_dir, r'_ignore\git-repo2')
        version = get_localver(working_dir=_working_dir)
        self.assertEqual('0.1.0+7f9de9327817', version)


class StorageTest(unittest.TestCase):

    def test_storage_is_instance_of_dict(self):
        s = dolfin.Storage()
        self.assertIsInstance(s, dict)

    def test_can_access_element_using_dot_notation(self):
        foo = dolfin.Storage()
        foo['bar'] = 'baz-qux-norf'
        self.assertEqual('baz-qux-norf', foo.bar)

    def test_can_set_element_using_dot_notation(self):
        foo = dolfin.Storage()
        foo.bar = 'baz-qux-norf'
        self.assertEqual('baz-qux-norf', foo['bar'])

    def test_access_using_unknown_member_returns_None(self):
        foo = dolfin.Storage()
        self.assertIsNone(foo.bar)

    def test_access_using_missing_key_returns_None(self):
        foo = dolfin.Storage()
        self.assertIsNone(foo['bar'])

    def test_can_be_pickled_and_unpickled(self):
        import pickle

        foo = dolfin.Storage(bar='baz')
        out = pickle.dumps(foo)
        self.assertIsNotNone(out)
        
        qux = pickle.loads(out)
        self.assertEqual('baz', qux.bar)

    def test_has_friendly_string_representation(self):
        foo = dolfin.Storage(bar='baz')
        self.assertTrue(repr(foo).startswith('<Storage'))
    
    def test_make_not_given_dict_or_sequence_throws(self):
        self.assertRaises(ValueError, dolfin.Storage.make, 'foo')

    def test_can_make_storage_from_dict(self):
        obj = dolfin.Storage.make(dict(foo='bar'))
        self.assertIsInstance(obj, dolfin.Storage)
        self.assertEqual('bar', obj.foo)

    def test_can_make_storage_from_nested_dicts(self):
        obj = dolfin.Storage.make(dict(
            baz = dict(
                quux = 'norf',
                meta = dict(
                    name = 'simple.conf',
                    path = r'c:\path\to\conf',
                )
            )
        ))
        self.assertIsInstance(obj, dolfin.Storage)
        self.assertIsInstance(obj.baz, dolfin.Storage)
        self.assertIsInstance(obj.baz.meta, dolfin.Storage)
    

class ConfigTest(unittest.TestCase):
    ""
    # base directory
    base_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_non_existing_file_causes_error(self):
        conf_path = r'c:\path\to\non\existing\file.conf'
        self.assertRaises(dolfin.ConfigNotFound, dolfin.Config, conf_path)

    def test_config_is_storage_instance(self):
        conf = dolfin.Config()
        self.assertIsInstance(conf, dolfin.Storage)

    def test_can_create_from_dict_instance(self):
        conf = dolfin.Config(foo='bar')
        self.assertIsNotNone(conf)
        self.assertEqual('bar', conf.foo)

    def test_can_create_from_file(self):
        conf_path = os.path.join(self.base_dir, 'simple.conf')
        conf = dolfin.Config(conf_path)
        self.assertDictEqual(conf, dict(
            foo = 'bar',
            baz = dolfin.Storage(quux = 'norf'),
            meta = dict(
                name = 'simple.conf',
                path = self.base_dir,
            ),
        ))

    def test_direct_config_override_file_config(self):
        conf_path = os.path.join(self.base_dir, 'simple.conf')
        conf = dolfin.Config(conf_path, baz=dict(spam = 'egg'))
        self.assertDictEqual(conf, dict(
            foo = 'bar',
            baz = dict(spam='egg'),
            meta = dict(
                name = 'simple.conf',
                path = self.base_dir,
            )
        ))
    
    def test_has_empty_meta_if_create_from_empty_init(self):
        conf = dolfin.Config()
        self.assertDictEqual(conf, dict(
            meta = dict(name=None, path=None)
        ))

    def test_has_empty_meta_if_not_create_from_file(self):
        conf = dolfin.Config(foo='bar')
        self.assertDictEqual(conf, dict(
            foo = 'bar',
            meta = dict(name=None, path=None),
        ))

    def test_has_meta_if_create_from_file(self):
        conf_path = os.path.join(self.base_dir, 'simple.conf')
        conf = dolfin.Config(conf_path)
        self.assertDictEqual(conf.meta, dict(
            name = 'simple.conf',
            path = self.base_dir,
        ))
    
    def test_all_dictlike_elements_are_storage(self):
        conf = dolfin.Config(foo='bar', baz=dict(spam='egg'))
        self.assertEqual('bar', conf.foo)
        self.assertEqual('egg', conf.baz.spam)
        self.assertIsNone(conf.meta.name)
        self.assertIsNone(conf.meta.path)

    def test_all_dictlike_elements_are_storage2(self):
        conf_path = os.path.join(self.base_dir, 'simple.conf')
        conf = dolfin.Config(conf_path)
        self.assertEqual('bar', conf.foo)
        self.assertEqual('norf', conf.baz.quux)
        self.assertEqual('simple.conf', conf.meta.name)
        self.assertEqual(self.base_dir, conf.meta.path)

    def test_can_create_from_complex_file_content(self):
        conf_path = os.path.join(self.base_dir, 'complex.conf')
        conf = dolfin.Config(conf_path)
        self.assertDictEqual(conf, dict(
            foo = 'bar',
            baz = ['quux', 'norf'],
            fix = dict(
                bug = [1, 'details go here'],
                inf = [2, 'details go here'],
                mix = [3, {
                    'bug': 'needs fixing...',
                    'inf': [1,2,3,4,5],
                    'all': dolfin.Storage(name=11),
                }]
            ),
            meta = dict(
                name = 'complex.conf',
                path = self.base_dir,
            )
        ))
    
    def test_can_register_default_config_values(self):
        conf = dolfin.Config()
        self.assertIsNone(conf.factory)

        dolfin.Config.register_defaults(
            factory = {
                'name': 'X-Factory',
                'location': 'X-Location',
            }
        )
        self.assertEqual('X-Factory', conf.factory.name)
    
    def test_can_register_default_config_functions(self):
        conf = dolfin.Config()
        self.assertIsNone(conf.factory)

        dolfin.Config.register_func_default(
            key='factory',
            function=lambda s,k: k + '-location'
        );
        self.assertEqual('factory-location', conf.factory)


class FakeCommand(dolfin.Command):
    
    prog = 'fake'
    desc = 'This is a fake implementation of the Command class'

    def __init__(self):
        self.p = None
        self.register = set()

    def _execute(self, args):
        self.register.add('_execute')
        return super(FakeCommand, self)._execute(args)
        
    def _create_parser(self):
        if self.p == None:
            from argparse import ArgumentParser
            
            p = ArgumentParser(prog=self.prog, description=self.desc)
            add = lambda *a, **k: p.add_argument(*a, **k)
            add('-p', '--port', type=int, default=None, help='server port')
            add('--host', help='server hostname')
            add('-s', '--show', action='store_true', help='show server details')
            self.register.add('_create_parser')
            self.p = p
        return self.p
    
    def _handle(self, args):
        self.register.add('_handle')
        if args.show:
            return "server='%s:%s'" % (args.port or 80, args.host or 'localhost')


class CommandTest(unittest.TestCase):
    
    def test_cannot_create_abstract_command(self):
        self.assertRaises(TypeError, dolfin.Command)

    def test_cannot_create_abstract_subcommand(self):
        self.assertRaises(TypeError, dolfin.SubCommand)

    def test_are_best_invoked_using_run_from_argv(self):
        cmd = FakeCommand()
        self.assertEqual(0, len(cmd.register))
        cmd.run_from_argv(['-p', '8080', '-s'])

        self.assertEqual(3, len(cmd.register))
        self.assertTrue(
            '_execute' in cmd.register and
            '_create_parser' in cmd.register and
            '_handle' in cmd.register
        )
