"""Exercise input guards and fresh-host check mode through real Ansible."""
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class NginxContractTests(unittest.TestCase):
    def run_play(self, variables, tasks=None, start_at=None, check=False):
        with tempfile.TemporaryDirectory(prefix='nginx-contract-') as tmp:
            play = {'name': 'Exercise the nginx role contract', 'hosts': 'localhost',
                    'connection': 'local', 'gather_facts': False, 'vars': variables}
            if tasks is None:
                play['roles'] = [{'role': str(ROOT / 'roles/nginx')}]
            else:
                play['tasks'] = tasks
            path = Path(tmp) / 'check.yml'
            path.write_text(yaml.safe_dump([play], sort_keys=False))
            command = ['ansible-playbook', '-i', 'localhost,', str(path)]
            if start_at:
                command += ['--start-at-task', start_at]
            if check:
                command += ['--check']
            return subprocess.run(command, capture_output=True, text=True, timeout=60)

    def run_guard(self, **overrides):
        defaults = yaml.safe_load((ROOT / 'roles/nginx/defaults/main.yml').read_text())
        defaults.update(overrides)
        guard = yaml.safe_load((ROOT / 'roles/nginx/tasks/main.yml').read_text())[0]
        return self.run_play(defaults, [guard])

    def test_standard_role_inputs_pass(self):
        result = self.run_guard()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unsafe_document_roots_fail(self):
        for root in ['/web/../etc', '/web/./content', '//', '/', '/web;include', '/web path']:
            with self.subTest(root=root):
                self.assertNotEqual(self.run_guard(nginx_docroot=root).returncode, 0)

    def test_invalid_listen_ports_fail(self):
        for port in [0, -1, 65536]:
            with self.subTest(port=port):
                self.assertNotEqual(self.run_guard(nginx_listen_port=port).returncode, 0)

    @unittest.skipIf(Path('/etc/nginx/nginx.conf').exists(), 'Requires a host without nginx configuration')
    def test_fresh_host_configuration_phase_is_safe_in_check_mode(self):
        # Start after package management to reproduce the state left by a
        # simulated installation without depending on the operator OS repositories.
        result = self.run_play({}, start_at='main | Inspect the installed nginx configuration', check=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(Path('/etc/nginx/nginx.conf').exists())
        self.assertIn('changed=0', result.stdout)


if __name__ == '__main__':
    unittest.main()
