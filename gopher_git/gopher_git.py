import os
import sys
import subprocess
from termcolor import colored
from typing import Any
from dotenv import load_dotenv


class GopherGit:
    def __init__(self, projects_path: str, projects_collect_strategy: str):
        self._projects_path = projects_path
        self._projects_collect_strategy = projects_collect_strategy

    @staticmethod
    def _get_strategy_types() -> list[str]:
        return ['all', 'changed']

    def _verify_inputs(self, files_path: str, strategy: str) -> None:
        strategy_types: list[str] = self._get_strategy_types()
        if not os.path.isdir(files_path):
            sys.exit(f'File path given, "{files_path}", is not valid')
        elif strategy not in self._get_strategy_types():
            sys.exit(f'File path is valid, but project search strategy was not\n Strategy options are {strategy_types}')

    @staticmethod
    def _is_strategy_collect_changed_projects(projects_collect_strategy: str):
        return projects_collect_strategy.lower() == 'changed'

    def run(self):
        try:
            self._verify_inputs(self._projects_path, self._projects_collect_strategy)
            git_projects = self._get_git_projects(self._projects_path)
            print('')
            for git_project in git_projects:
                project_name = colored(f' {git_project["directory_name"]} ', 'white', 'on_cyan')
                git_log: str = self._get_latest_git_commit_summary(git_project["directory_path"])
                git_status: dict = self._get_git_status(git_project["directory_path"])
                git_branch: str = colored(f'{git_status["project_branch"]}', 'cyan')
                is_git_branch_state_changed: bool = 'Your branch is up to date' not in git_status['project_branch_state']
                raw_status_output: str = git_status['raw_status_output']
                _projects_comparator: bool = True

                if self._is_strategy_collect_changed_projects(self._projects_collect_strategy):
                    _projects_comparator = 'nothing to commit' not in raw_status_output or is_git_branch_state_changed

                if _projects_comparator:
                    print(f'{project_name}')
                    print(f'  {git_branch} {git_project["directory_path"]}')
                    if is_git_branch_state_changed:
                        print(f'  {git_status["project_branch_state"]}')
                    print(f'  Last Commit {git_log}')

                    if len(git_status['modified_files']):
                        print(f'\n  Changes (staged and non-staged):')
                        for modified_file in git_status['modified_files']:
                            split_output_text: list[str] = modified_file.split(':')
                            modified_file_name: str = colored(f'{split_output_text[1].strip()}', 'yellow')
                            print(f'{split_output_text[0]}: {modified_file_name}')

                    if len(git_status['untracked_files']):
                        print(f'\n  Untracked Files:')
                        for untracked_file in git_status['untracked_files']:
                            file_name: str = colored(f' {untracked_file} ', 'yellow')
                            print(f'{file_name}')
                    print('')
        except TypeError as type_error:
            print(f'Received TypeError: {type_error}')
        sys.exit()

    @staticmethod
    def _get_git_status(project_path: str) -> dict:
        untracked_files_start: int = -1
        untracked_files_end: int = -1
        modified_files: list[str] = []
        untracked_files: list[str] = []

        temp = subprocess.Popen(['git', 'status'], cwd=project_path, stdout=subprocess.PIPE)
        subprocess_output: tuple[bytes, Any] = temp.communicate()
        raw_status_output: str = subprocess_output[0].decode()
        output_text_list: list[str] = raw_status_output.split('\n')

        project_branch: str = output_text_list[0].split(' ')[2]
        project_branch_state: str = output_text_list[1]
        for index, output_text in enumerate(output_text_list):
            if 'modified' in output_text:
                modified_files.append(output_text)
            elif 'Untracked files' in output_text:
                untracked_files_start = index+2
            elif untracked_files_start > -1 and '' == output_text:
                untracked_files_end = index
                break

        modified_files = list(set(modified_files))
        if untracked_files_start > -1:
            untracked_files = output_text_list[untracked_files_start:untracked_files_end]

        return {
            'project_branch': project_branch,
            'project_branch_state': project_branch_state,
            'raw_status_output': raw_status_output,
            'modified_files': modified_files,
            'untracked_files': untracked_files
        }

    @staticmethod
    def _get_latest_git_commit_summary(project_path: str) -> str:
        temp = subprocess.Popen(['git', 'log'], cwd=project_path, stdout=subprocess.PIPE)
        subprocess_output: tuple[bytes, Any] = temp.communicate()
        raw_log_output: str = subprocess_output[0].decode()
        output_text_list: list[str] = raw_log_output.split('\n')

        commit_message: str = output_text_list[4].strip()
        commit_date: str = output_text_list[2].split(':', 1)[1].strip()
        commit_author: str = output_text_list[1].split(' ')[1]
        commit_hash: str = colored(f'{output_text_list[0].split(" ")[1][0:7]}', 'magenta')
        latest_commit_summary: str = f'{commit_author} - {commit_hash} ({commit_date}): {commit_message}'
        return latest_commit_summary

    def _get_git_projects(self, projects_path: str) -> list[dict]:
        git_projects: list[dict] = []
        git_projects_path_list = self.get_git_project_path_list(projects_path)
        for directory in git_projects_path_list:
            if '.git' in directory[1]:
                directory_name: str = directory[0].split('/')[-1]
                git_projects.append({
                    'directory_name': directory_name,
                    'directory_path': directory[0],
                    'subdirectories': directory[1],
                    'files': directory[2]
                })
        git_projects.sort(key=lambda project: project['directory_name'])
        return git_projects

    @staticmethod
    def get_git_project_path_list(files_path: str) -> list[tuple]:
        return [path for path in os.walk(files_path)]


if __name__ == '__main__':
    try:
        load_dotenv()
        PROJECTS_DIR: str = str(os.getenv('PROJECTS_DIR'))
        PROJECTS_COLLECT_STRATEGY: str = str(os.getenv('PROJECTS_COLLECT_STRATEGY'))

        if len(sys.argv) == 2:
            if sys.argv[1] == '-h' or 'help' in sys.argv[1]:
                print('\nUsage: gogit [-h output usage] <projects_parent_directory> <project_search_strategy>\n\n'
                      'If search strategy, or projects parent directory is left out of command call, '
                      'they will be loaded from default .env file\n')
            else:
                gopher_git_job = GopherGit(sys.argv[1], PROJECTS_COLLECT_STRATEGY)
                gopher_git_job.run()
        elif len(sys.argv) == 3:
            gopher_git_job = GopherGit(sys.argv[1], sys.argv[2])
            gopher_git_job.run()
        else:
            gopher_git_job = GopherGit(PROJECTS_DIR, PROJECTS_COLLECT_STRATEGY)
            gopher_git_job.run()

    except TypeError:
        print(f'Received TypeError: Check that the .env project file is configured correctly')
        sys.exit()
