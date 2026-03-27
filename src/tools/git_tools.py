import subprocess
import os
from typing import List, Optional

class GitTools:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)

    def _run_git_command(self, args: List[str]) -> tuple:
        """执行 Git 命令，返回 (stdout, stderr, returncode)"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), -1

    def commit_and_push(self, message: str, patterns: List[str]) -> dict:
        """
        提交并推送修改，只允许 patterns 指定的文件或目录
        返回 {'success': bool, 'error': str, 'commit_hash': str}
        """
        # 校验 commit 消息
        if not self._validate_commit_message(message):
            return {'success': False, 'error': 'Invalid commit message'}

        # 检查是否有未提交的修改
        stdout, stderr, code = self._run_git_command(['status', '--porcelain'])
        if code != 0:
            return {'success': False, 'error': f'Git status failed: {stderr}'}
        if not stdout.strip():
            return {'success': False, 'error': 'No changes to commit'}

        # 添加指定文件/目录
        for pattern in patterns:
            # 确保 pattern 在仓库路径内（防止路径遍历）
            full_pattern = os.path.join(self.repo_path, pattern)
            if not full_pattern.startswith(self.repo_path):
                return {'success': False, 'error': f'Forbidden pattern: {pattern}'}
            self._run_git_command(['add', pattern])

        # 提交
        stdout, stderr, code = self._run_git_command(['commit', '-m', message])
        if code != 0:
            return {'success': False, 'error': f'Commit failed: {stderr}'}

        # 获取 commit hash
        commit_hash = self._get_latest_commit()

        # 推送
        stdout, stderr, code = self._run_git_command(['push'])
        if code != 0:
            # 推送失败时不回滚，但报告错误
            return {'success': False, 'error': f'Push failed: {stderr}', 'commit_hash': commit_hash}

        return {'success': True, 'commit_hash': commit_hash}

    def _validate_commit_message(self, message: str) -> bool:
        """防止命令注入"""
        # 不允许包含可能被 shell 解释的字符
        forbidden = [';', '&&', '||', '`', '$', '\\']
        return not any(c in message for c in forbidden)

    def _get_latest_commit(self) -> str:
        stdout, _, _ = self._run_git_command(['rev-parse', '--short', 'HEAD'])
        return stdout.strip()