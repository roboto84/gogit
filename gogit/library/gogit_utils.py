
import os
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any


class GogitUtils:
    @staticmethod
    def get_recursive_directory_files_and_subdir(files_path: str) -> list[tuple]:
        return [path for path in os.walk(files_path)]

    @staticmethod
    def is_strategy_collect_changed_projects(projects_collect_strategy: str):
        return projects_collect_strategy.lower() == 'changed'

    @staticmethod
    def raw_change_type(raw_change_type: str):
        git_change_types: dict = {
            'M': 'modified',
            'A': 'new file',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied',
            'U': 'unmerged'
        }
        return git_change_types.get(raw_change_type)

    @staticmethod
    def get_git_status(project_path: str, projects_collect_strategy: str) -> dict:
        # Using https://github.com/git/git/blob/master/wt-status.c#L287 and
        # https://git-scm.com/docs/git-status/2.6.7#_options
        git_change_types: list[str] = ['M', 'D', 'A', 'R', 'C', 'U']
        modified_files: list[dict] = []
        untracked_files: list[dict] = []

        git_status = subprocess.Popen(['git', 'status'], cwd=project_path, stdout=subprocess.PIPE)
        raw_status_output: str = git_status.communicate()[0].decode()
        git_status_output_text: list[str] = raw_status_output.split('\n')
        project_branch: str = ''
        project_branch_status: str = ''
        has_branch_changed_from_origin: bool = False

        if 'branch' in git_status_output_text[0]:
            project_branch: str = git_status_output_text[0].split(' ')[2]
        if 'branch' in git_status_output_text[1]:
            project_branch_status: str = git_status_output_text[1]
            has_branch_changed_from_origin: bool = 'Your branch is up to date' not in project_branch_status

        has_project_got_changes: bool = 'nothing to commit' not in raw_status_output or has_branch_changed_from_origin

        git_status_porcelain = subprocess.Popen(
            ['git', 'status', '--porcelain'],
            cwd=project_path,
            stdout=subprocess.PIPE
        )
        git_status_porcelain_output_text: list[str] = git_status_porcelain.communicate()[0].decode().split('\n')
        git_status_porcelain_output_text = list(filter(None, git_status_porcelain_output_text))

        if projects_collect_strategy != 'latest':
            for output_text in git_status_porcelain_output_text:
                output_text_split = output_text.split(' ')
                output_text_split = list(filter(None, output_text_split))
                output_first_letter: str = output_text_split[0][:1]
                if output_first_letter in git_change_types:
                    modified_files.append({
                        'short_type': output_text_split[0],
                        'long_type': GogitUtils.raw_change_type(output_first_letter),
                        'file_name': output_text_split[1]
                    })
                elif output_first_letter == '?':
                    untracked_files.append({
                        'type': output_text_split[0],
                        'file_name': output_text_split[1]
                    })

        return {
            'project_branch': project_branch,
            'project_branch_status': project_branch_status,
            'has_branch_changed': has_branch_changed_from_origin,
            'has_project_got_changes': has_project_got_changes,
            'modified_files': modified_files,
            'untracked_files': untracked_files
        }

    @staticmethod
    def get_latest_git_commit_summary(project_path: str) -> dict:
        try:
            temp = subprocess.Popen(['git', 'log'], cwd=project_path, stdout=subprocess.PIPE)
            subprocess_output: tuple[bytes, Any] = temp.communicate()
            raw_log_output: str = subprocess_output[0].decode()
            output_text_list: list[str] = raw_log_output.split('\n')
            current_date: datetime = datetime.now(timezone.utc)
            commit_tracking_index: int = -1
            commit_hash: str = ''
            commit_author: str = ''
            commit_date: str = ''
            commit_message: str = ''

            if raw_log_output != '':
                for index, log_element in enumerate(output_text_list):
                    element_split = log_element.split()
                    if len(element_split):
                        if 'commit' in element_split[0]:
                            if index != 0:
                                break
                            commit_hash = log_element.split()[1][0:7]
                        elif 'Author:' in element_split:
                            commit_author = ''.join(f'{author_part} ' for author_part in log_element.split()[1:-1]).rstrip()
                        elif 'Date:' in element_split:
                            commit_tracking_index = index
                            commit_date = log_element.split(':', 1)[1].strip()
                        elif commit_tracking_index != -1:
                            commit_message = log_element.strip()
                            break

                commit_datetime: datetime = datetime.strptime(commit_date, '%a %b %d %H:%M:%S %Y %z')
                time_since_commit: timedelta = current_date - commit_datetime

                return {
                    'commit_message':  commit_message,
                    'commit_date':  commit_datetime,
                    'time_since_commit':  time_since_commit,
                    'commit_author':  commit_author,
                    'commit_hash':  commit_hash
                }
            else:
                return {}
        except Exception as error:
            print(f'Received exception: {project_path}: {error}')

    @staticmethod
    def get_git_projects(projects_path: str) -> list[dict]:
        git_projects: list[dict] = []
        directory_files_and_subdir_list: list[tuple] = GogitUtils.get_recursive_directory_files_and_subdir(
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
