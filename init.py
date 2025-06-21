#!/usr/bin/env python3

import argparse
import random
import re
import shutil
import string
import subprocess
import sys
import venv
from os import chdir
from pathlib import Path


srcpath = Path(__file__).parent


def create_dir(path: Path, force: bool = False):
    if path.exists():
        if not path.is_dir():
            print(f"Path {path} exists and is not a directory; aborting.")
            sys.exit(1)
        if not force:
            print(f"Path {path} already exists, aborting. (Use --force to use it anyway)")
            sys.exit(1)
        print(f"Path {path} already exists, using it anyway because --force.")
    else:
        path.mkdir(parents=True)
        print(f"Created project directory: {path}")


def copy_pyproject_toml(root_path: Path, project_name: str, description: str):
    with root_path.joinpath("pyproject.toml").open("wt", encoding="utf8") as outfile:
        with srcpath.joinpath("pyproject.toml").open("rt", encoding="utf8") as infile:
            section = ""
            for line in infile:
                if line.startswith("[") and line.strip().endswith("]"):
                    section = line.strip("[]\n")
                if section == "project" and re.match(r"^name *=.*", line):
                    outfile.write(f"name = \"{project_name}\"\n")
                elif section == "project" and re.match(r"^description *=.*", line):
                    outfile.write(f"description = \"{description}\"\n")
                else:
                    outfile.write(line)
    print("Wrote pyproject.toml.")


def copy_package_json(destpath: Path, project_name: str):
    with destpath.joinpath("package.json").open("wt", encoding="utf8") as outfile:
        with srcpath.joinpath("package.json").open("rt", encoding="utf8") as infile:
            for line in infile:
                if re.match(r"^\s*\"name\"", line):
                    outfile.write(f"  \"name\": \"{project_name}\",\n")
                else:
                    outfile.write(line)
    print("Wrote package.json.")


def copy_frontend_files(destpath: Path, project_name: str):
    shutil.copytree(srcpath.joinpath("assets").absolute(), destpath.joinpath("assets").absolute())
    shutil.copytree(srcpath.joinpath("deployment").absolute(), destpath.joinpath("deployment").absolute())
    copy_package_json(destpath=destpath, project_name=project_name)
    for filename in (
        ".eslintrc.cjs",
        "tsconfig.json",
        "webpack.base.config.ts",
        "webpack.dev.config.ts",
        "webpack.prod.config.ts",
    ):
        shutil.copy(srcpath.joinpath(filename).absolute(), destpath.joinpath(filename).absolute())
    print("Wrote frontend stuff.")


def generate_env_file(root_path: Path):
    secret_chars = (string.ascii_lowercase + string.digits + string.punctuation).replace("\"", "")
    secret = "".join(random.choices(secret_chars, k=50))
    with root_path.joinpath(".env").open("wt", encoding="utf8") as f:
        f.write(f"DJANGO_SECRET_KEY=\"{secret}\"\n")
        f.write("DEBUG=true\n")
    print("Wrote .env.")


def copy_base_files(root_path: Path, project_name: str, description: str):
    generate_env_file(root_path=root_path)
    copy_pyproject_toml(root_path=root_path, project_name=project_name, description=description)
    shutil.copytree(
        srcpath.joinpath("src").absolute(),
        root_path.joinpath("src").absolute(),
        ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"),
    )
    for filename in (".flake8", ".gitignore", "LICENSE"):
        shutil.copy(srcpath.joinpath(filename).absolute(), root_path.joinpath(filename).absolute())
    print("Copied base files.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name")
    parser.add_argument("directory", help="Project root dir (default: cwd/project_name)", nargs="?")
    parser.add_argument("-d", "--description", nargs="?", default="")
    parser.add_argument("-nf", "--no-frontend", help="Don't copy frontend stuff.", action="store_true")
    parser.add_argument("-ng", "--no-git", help="Don't run git init.", action="store_true")
    parser.add_argument("-f", "--force", help="Continue even if destination directory exists.", action="store_true")

    args = parser.parse_args()

    if not re.match(r"^[a-zA-Z0-9\-_]+$", args.project_name):
        print("Project name can only contain alphanumeric characters, hyphens, and underscores.")
        sys.exit(1)

    if args.directory:
        root_path = Path(args.directory)
    else:
        root_path = Path(args.project_name)

    create_dir(path=root_path, force=args.force)
    print(f"Using path `{root_path.absolute()}`.")
    copy_base_files(root_path=root_path, project_name=args.project_name, description=args.description)
    if not args.no_frontend:
        copy_frontend_files(destpath=root_path, project_name=args.project_name)
    chdir(root_path)
    venv.create(".venv", with_pip=True)
    print(f"Created virtual environment in `{root_path.absolute() / '.venv'}`.")
    if not args.no_frontend:
        print("Running `npm install`.")
        subprocess.run("npm i", shell=True, check=True)
    subprocess.run(". .venv/bin/activate && pip install -e .[dev]", shell=True, check=True)
    if not args.no_git:
        print("Running `git init`.")
        subprocess.run("git init", shell=True, check=True)


if __name__ == "__main__":
    main()
