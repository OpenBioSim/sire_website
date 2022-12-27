
import sire as project
import sys
import os
import subprocess
import shlex

branch = project.__branch__
release = project.__version__
version = project.__version__.split("+")[0]
repository = project.__repository__
revisionid = project.__revisionid__

if version.find("untagged") != -1:
    print("This is an untagged branch")
    version = project.__manual_version__

print(f"Build docs for branch {branch} version {version}")

# we will only build docs for the main and devel branches
# (as these are moved into special locations)

force_build_docs = os.environ["FORCE_BUILD_DOCS"]

if branch not in ["main", "devel"]:
    if branch.find(version) != -1:
        print(f"Building the docs for tag {version}")
        is_tagged_release = True
    elif force_build_docs:
        print(f"Force-building docs for branch {branch}")
    else:
        print(f"We don't build the docs for branch {branch}")
        sys.exit(0)

os.environ["PROJECT_VERSION"] = version
os.environ["PROJECT_BRANCH"] = branch
os.environ["PROJECT_RELEASE"] = release
os.environ["PROJECT_REPOSITORY"] = repository
os.environ["PROJECT_REVISIONID"] = revisionid


def run_command(cmd, dry=False):
    """Run the passed shell command"""
    if dry:
        print(f"[DRY-RUN] {cmd}")
        return

    print(f"[EXECUTE] {cmd}")

    try:
        args = shlex.split(cmd)
        subprocess.run(args).check_returncode()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(-1)

# install doc dependencies
reqs = " ".join([line.lstrip().rstrip() for line in open("requirements.txt", "r").readlines()])

print(f"Installing doc requirements: {reqs}")

run_command(f"mamba install {reqs}")

# make the documentation
run_command("make")
