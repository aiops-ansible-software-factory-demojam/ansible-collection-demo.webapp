"""Execute production source/scope and health assertions without changing hosts."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import yaml
ROOT = Path(__file__).resolve().parents[1]

class WebappPromotionTests(unittest.TestCase):
    def setUp(self):
        self.v = {'awx_job_id': 13, 'awx_workflow_job_id': 10, 'awx_workflow_job_name': 'webapp_promote',
            'awx_project_revision': 'a' * 40, 'webapp_candidate_sha': 'a' * 40, 'webapp_issue_number': 1, 'webapp_pr_number': 2,
            'webapp_release_contract': {'schema_version': 1, 'repository': 'demo-owner/ansible-collection-demo.webapp',
                'source_revision': 'a' * 40, 'issue_number': 1, 'pr_number': 2, 'hosts': ['localhost']}}
    def run_tasks(self, values, tasks, passes=True):
        with tempfile.TemporaryDirectory() as tmp:
            inv = Path(tmp)/'inventory.yml'; inv.write_text(yaml.safe_dump({'webapps': {'hosts': {'localhost': {'ansible_connection': 'local'}}}}))
            play = Path(tmp)/'play.yml'; play.write_text(yaml.safe_dump([{'name': 'Exercise exact nginx promotion guards',
                'hosts': 'webapps', 'gather_facts': False, 'tasks': tasks}]))
            r = subprocess.run(['ansible-playbook', '-i', str(inv), str(play), '-e', json.dumps(values)], capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode == 0, passes, r.stdout + r.stderr)
    def test_exact_native_web_source_and_scope_pass(self):
        self.run_tasks(self.v, yaml.safe_load((ROOT/'playbooks/tasks/validate-promotion.yml').read_text()))
    def test_pinned_job_with_later_default_merge_revision_passes(self):
        v = dict(self.v, awx_project_revision='b' * 40, awx_job_scm_branch='a' * 40)
        self.run_tasks(v, yaml.safe_load((ROOT/'playbooks/tasks/validate-promotion.yml').read_text()))
    def test_matching_default_revision_cannot_hide_wrong_or_mutable_job_override(self):
        for branch in ['main', 'feature/issue-1', 'b' * 40, '']:
            with self.subTest(branch=branch):
                self.run_tasks(dict(self.v, awx_job_scm_branch=branch),
                    yaml.safe_load((ROOT/'playbooks/tasks/validate-promotion.yml').read_text()), False)
    def test_direct_launch_wrong_source_incident_or_hosts_fail_before_guest_access(self):
        tasks = yaml.safe_load((ROOT/'playbooks/tasks/validate-promotion.yml').read_text())
        for field in ['workflow','source','incident','hosts','repository']:
            v=copy.deepcopy(self.v)
            if field=='workflow': v['awx_workflow_job_name']='invoice_promote'
            if field=='source': v['awx_project_revision']='b'*40
            if field=='incident': v['webapp_issue_number']=99
            if field=='hosts': v['webapp_release_contract']['hosts']=['python-host']
            if field=='repository': v['webapp_release_contract']['repository']='demo-owner/ansible-collection-demo.pythonapp'
            with self.subTest(field=field): self.run_tasks(v,tasks,False)
    def test_permissive_or_wrong_page_is_not_recovery(self):
        tasks = [t for t in yaml.safe_load((ROOT/'playbooks/tasks/verify-promotion.yml').read_text()) if 'ansible.builtin.assert' in t]
        values = {'ansible_facts': {'selinux': {'status':'enabled','mode':'enforcing'}},
            'nginx_index_content':'Expected page', 'webapp_promotion_http': {'content':'Expected page'}}
        self.run_tasks(values,tasks)
        for field in ['selinux','page']:
            v=copy.deepcopy(values)
            if field=='selinux':v['ansible_facts']['selinux']['mode']='permissive'
            else:v['webapp_promotion_http']['content']='Wrong application'
            with self.subTest(field=field):self.run_tasks(v,tasks,False)
    def test_local_reviewed_role_is_reached_only_after_source_guard(self):
        play=yaml.safe_load((ROOT/'playbooks/promote_webapp.yml').read_text())[0]
        self.assertEqual(play['hosts'],'webapps')
        self.assertEqual(play['tasks'][0]['ansible.builtin.import_tasks'],'tasks/validate-promotion.yml')
        self.assertEqual(play['tasks'][1]['ansible.builtin.import_role']['name'],'nginx')
        self.assertEqual(play['tasks'][2]['ansible.builtin.meta'],'flush_handlers')
