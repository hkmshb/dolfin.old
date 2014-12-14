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
