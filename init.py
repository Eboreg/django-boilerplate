#!/usr/bin/env python3

from os import chdir
import random
import shutil
from pathlib import Path
import re
import string
import subprocess
import sys
import argparse
import venv

srcpath = Path(__file__).parent


def create_dir(dirname: str, parent: str) -> Path:
    path = Path(parent).joinpath(dirname)
    if path.exists():
        print("Path already exists, aborting.")
        sys.exit(1)
    path.mkdir()
    return path


def copy_pyproject_toml(destpath: Path, project_name: str, description: str):
    with destpath.joinpath("pyproject.toml").open("wt", encoding="utf8") as outfile:
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


def generate_env_file(destpath: Path):
    secret_chars = (string.ascii_lowercase + string.digits + string.punctuation).replace("\"", "")
    secret = "".join(random.choices(secret_chars, k=50))
    with destpath.joinpath(".env").open("wt", encoding="utf8") as f:
        f.write(f"DJANGO_SECRET_KEY=\"{secret}\"\n")
        f.write("DEBUG=true\n")
    print("Wrote .env.")


def copy_base_files(destpath: Path, project_name: str, description: str):
    generate_env_file(destpath=destpath)
    copy_pyproject_toml(destpath=destpath, project_name=project_name, description=description)
    shutil.copytree(
        srcpath.joinpath("src").absolute(),
        destpath.joinpath("src").absolute(),
        ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"),
    )
    for filename in (".flake8", ".gitignore", "LICENSE"):
        shutil.copy(srcpath.joinpath(filename).absolute(), destpath.joinpath(filename).absolute())
    print("Copied base files.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name")
    parser.add_argument("parent", help="Parent directory of the project")
    parser.add_argument("-d", "--description", nargs="?", default="")
    parser.add_argument("-nf", "--no-frontend", help="Don't copy frontend stuff.", action="store_true")
    parser.add_argument("-ng", "--no-git", help="Don't run git init.", action="store_true")

    args = parser.parse_args()
    destpath = create_dir(args.project_name, args.parent)
    copy_base_files(destpath=destpath, project_name=args.project_name, description=args.description)
    if not args.no_frontend:
        copy_frontend_files(destpath=destpath, project_name=args.project_name)
    chdir(destpath)
    venv.create(".venv", with_pip=True)
    print("Created virtual environment in .venv.")
    if not args.no_frontend:
        subprocess.run("npm i", shell=True, check=True)
    subprocess.run(". .venv/bin/activate && pip install -e .[dev]", shell=True, check=True)
    if not args.no_git:
        subprocess.run("git init", shell=True, check=True)


if __name__ == "__main__":
    main()
