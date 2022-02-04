
import os
import subprocess
from typing import Any


class GopherGitUtils:
    @staticmethod
    def get_recursive_directory_files_and_subdir(files_path: str) -> list[tuple]:
        return [path for path in os.walk(files_path)]

    @staticmethod
    def is_strategy_collect_changed_projects(projects_collect_strategy: str):
        return projects_collect_strategy.lower() == 'changed'

    @staticmethod
    def get_git_status(project_path: str) -> dict:
        untracked_files_start: int = -1
        untracked_files_end: int = -1
        modified_files: list[str] = []
        untracked_files: list[str] = []

        temp = subprocess.Popen(['git', 'status'], cwd=project_path, stdout=subprocess.PIPE)
        subprocess_output: tuple[bytes, Any] = temp.communicate()
        raw_status_output: str = subprocess_output[0].decode()
        output_text_list: list[str] = raw_status_output.split('\n')
        project_branch: str = output_text_list[0].split(' ')[2]
        project_branch_status: str = output_text_list[1]
        has_branch_changed: bool = 'Your branch is up to date' not in project_branch_status
        has_project_got_changes: bool = 'nothing to commit' not in raw_status_output or has_branch_changed

        for index, output_text in enumerate(output_text_list):
            if 'modified' in output_text:
                modified_files.append(output_text)
            elif 'Untracked files' in output_text:
                untracked_files_start = index + 2
            elif untracked_files_start > -1 and '' == output_text:
                untracked_files_end = index
                break

        if untracked_files_start > -1:
            untracked_files = output_text_list[untracked_files_start:untracked_files_end]

        return {
            'project_branch': project_branch,
            'project_branch_status': project_branch_status,
            'has_branch_changed': has_branch_changed,
            'has_project_got_changes': has_project_got_changes,
            'modified_files': list(set(modified_files)),
            'untracked_files': untracked_files
        }

    @staticmethod
    def get_latest_git_commit_summary(project_path: str) -> dict:
        temp = subprocess.Popen(['git', 'log'], cwd=project_path, stdout=subprocess.PIPE)
        subprocess_output: tuple[bytes, Any] = temp.communicate()
        raw_log_output: str = subprocess_output[0].decode()
        output_text_list: list[str] = raw_log_output.split('\n')

        return {
            'commit_message':  output_text_list[4].strip(),
            'commit_date':  output_text_list[2].split(':', 1)[1].strip(),
            'commit_author':  output_text_list[1].split(' ')[1],
            'commit_hash':  output_text_list[0].split(" ")[1][0:7]
        }

    @staticmethod
    def get_git_projects(projects_path: str) -> list[dict]:
        git_projects: list[dict] = []
        directory_files_and_subdir_list: list[tuple] = GopherGitUtils.get_recursive_directory_files_and_subdir(
            projects_path
        )
        for directory_data in directory_files_and_subdir_list:
            if '.git' in directory_data[1]:
                directory_name: str = directory_data[0].split('/')[-1]
                git_projects.append({
                    'directory_name': directory_name,
                    'directory_path': directory_data[0],
                    'subdirectories': directory_data[1],
                    'files': directory_data[2]
                })
        git_projects.sort(key=lambda project: project['directory_name'])
        return git_projects
