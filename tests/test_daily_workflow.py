"""Exercise the real daily workflow Git step against temporary local remotes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml


class DailyWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workflow = Path(__file__).resolve().parents[1] / '.github/workflows/bot.yml'
        document = yaml.safe_load(workflow.read_text(encoding='utf-8'))
        steps = document['jobs']['run-command-center']['steps']
        matches = [step for step in steps if step.get('name') == 'Commit & Push reports.json']
        if len(matches) != 1:
            raise AssertionError('Expected exactly one report persistence step')
        cls.script = matches[0]['run']
        cls.git = shutil.which('git')
        if cls.git is None:
            raise AssertionError('Git is required')

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='daily-workflow-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / 'repo'
        self.remote = self.root / 'remote.git'
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        self.env.update({
            'GIT_CONFIG_GLOBAL': str(self.root / 'gitconfig'),
            'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_ALLOW_PROTOCOL': 'file',
            'GIT_TERMINAL_PROMPT': '0',
        })
        self.checked('init', '--bare', str(self.remote), cwd=self.root)
        self.checked('init', '-b', 'main', str(self.repo), cwd=self.root)
        self.checked('config', 'user.name', 'Offline Test')
        self.checked('config', 'user.email', 'offline@example.invalid')
        (self.repo / 'reports.json').write_text('[]\n', encoding='utf-8')
        self.checked('add', 'reports.json')
        self.checked('commit', '-m', 'initial')
        self.checked('remote', 'add', 'origin', str(self.remote))
        self.checked('push', '-u', 'origin', 'main')
        self.before = self.checked('rev-parse', 'HEAD')
        self.calls = self.root / 'calls'
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        wrapper = bin_dir / 'git'
        wrapper.write_text(
            '#!/bin/bash\n'
            'printf "%s\\n" "$1" >> "$GIT_TEST_CALLS"\n'
            'if [[ "$1" == "$GIT_TEST_FAIL" ]]; then exit 44; fi\n'
            'exec "$GIT_TEST_REAL" "$@"\n', encoding='utf-8'
        )
        wrapper.chmod(0o755)
        self.env.update({
            'PATH': str(bin_dir) + os.pathsep + self.env['PATH'],
            'GIT_TEST_CALLS': str(self.calls),
            'GIT_TEST_REAL': self.git,
            'GIT_TEST_FAIL': '',
        })

    def checked(self, *args, cwd=None):
        result = subprocess.run(
            [self.git, *args], cwd=cwd or self.repo, env=self.env,
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def execute(self):
        return subprocess.run(
            ['bash', '--noprofile', '--norc', '-e', '-o', 'pipefail', '-c', self.script],
            cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=15,
        )

    def change_report(self):
        (self.repo / 'reports.json').write_text('[{"test": true}]\n', encoding='utf-8')

    def remote_head(self):
        return self.checked('--git-dir', str(self.remote), 'rev-parse', 'refs/heads/main')

    def hook(self, path):
        path.write_text('#!/bin/sh\nexit 42\n', encoding='utf-8')
        path.chmod(0o755)

    def test_unchanged_report_skips_commit_and_push(self):
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('commit', self.calls.read_text().splitlines())
        self.assertNotIn('push', self.calls.read_text().splitlines())
        self.assertEqual(self.checked('rev-parse', 'HEAD'), self.before)
        self.assertEqual(self.remote_head(), self.before)

    def test_changed_report_is_committed_and_pushed(self):
        self.change_report()
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        after = self.checked('rev-parse', 'HEAD')
        self.assertNotEqual(after, self.before)
        self.assertEqual(self.remote_head(), after)
        self.assertEqual(self.checked('rev-list', '--count', f'{self.before}..HEAD'), '1')
        self.assertEqual(
            self.checked('--git-dir', str(self.remote), 'show', 'main:reports.json'),
            '[{"test": true}]',
        )

    def check_command_failure(self, command):
        self.change_report()
        self.env['GIT_TEST_FAIL'] = command
        result = self.execute()
        self.assertEqual(result.returncode, 44, result.stderr)
        calls = self.calls.read_text().splitlines()
        self.assertIn(command, calls)
        self.assertNotIn('commit', calls)
        self.assertNotIn('push', calls)
        self.assertEqual(self.checked('rev-parse', 'HEAD'), self.before)
        self.assertEqual(self.remote_head(), self.before)

    def test_add_failure_stops_step(self):
        self.check_command_failure('add')

    def test_diff_error_is_not_treated_as_changes(self):
        self.check_command_failure('diff')

    def test_commit_failure_stops_before_push(self):
        self.change_report()
        self.hook(self.repo / '.git/hooks/pre-commit')
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('commit', self.calls.read_text().splitlines())
        self.assertNotIn('push', self.calls.read_text().splitlines())
        self.assertEqual(self.checked('rev-parse', 'HEAD'), self.before)
        self.assertEqual(self.remote_head(), self.before)

    def test_push_failure_is_reported(self):
        self.change_report()
        self.hook(self.remote / 'hooks/pre-receive')
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('push', self.calls.read_text().splitlines())
        self.assertNotEqual(self.checked('rev-parse', 'HEAD'), self.before)
        self.assertEqual(self.remote_head(), self.before)


if __name__ == '__main__':
    unittest.main()
