<h1 align="center">gogit</h1>

<div align="center">
	<img src="assets/gogit.png" width="250" title="gogit logo">
</div>

## About
`gogit` is a tool that shows current git project information given a directory containing one or more git project directories.

## Requirements
- [pipx](https://github.com/pypa/pipx "pipx") or [poetry](https://github.com/python-poetry/poetry "poetry")
- Python 3.10^

## Install
- With pipx:
    ```
    pipx install git+https://github.com/roboto84/gogit.git
    ```

or

- Local build with poetry:
    ```
    git clone https://github.com/roboto84/gogit.git
    ```
    ```
    cd gogit
    ```
    ```
    poetry install
    ```

## Usage
- With pipx
    ```
    gogit
    ```

- With poetry
    ```
    poetry run gogit
    ```

## Options
| Flag | Title | Description | Use
|------|-------|-------------|-----
| `-h` | help | Show help menu. | *`gogit -h`*
| `all` | all | Returns a summary of all Git projects found in given parent search directory. |*`gogit all`*
| `changed` | changed | Returns only Git projects in which a change was detected. <br/>(i.e. modified and untracked files) |*`gogit changed`*
| `latest` | latest | Returns all Git projects ignoring changes. <br/>(i.e. useful for getting basic project information such as latest commit) |*`gogit latest`*

## Commit Conventions
Git commits follow [Conventional Commits](https://www.conventionalcommits.org) message style as explained in detail on their website.

<br/>
<sup>
    <a href="https://www.flaticon.com/free-icons/version-control" title="version control icons">
        gogit icon created by edt.im - Flaticon
    </a>
</sup>
