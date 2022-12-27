import sire as project
import sys
import os
from distutils import dir_util
import glob
import json

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
is_tagged_release = False

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

if not os.path.exists("./gh-pages"):
    print("You have not checked out the gh-pages branch correctly!")
    sys.exit(-1)

# if this is the main branch, then copy the docs to both the root
# directory of the website, and also to the 'versions/version' directory
if is_tagged_release or (branch == "main"):
    print(f"Copying main docs to gh-pages")
    dir_util.copy_tree("build/html/", "gh-pages/")

    if is_tagged_release:
        print(f"Copying main docs to gh-pages/versions/{version}")
        dir_util.copy_tree("build/html/", f"gh-pages/versions/{version}/")

elif branch == "devel":
    dir_util.copy_tree("build/html/", "gh-pages/versions/devel/")

else:
    dir_util.copy_tree("build/html/", f"gh-pages/versions/{branch}/")


# now write the versions.json file
versions = []
versions.append(["latest", "/"])
versions.append(["development", "/versions/devel/"])

vs = {}

for version in glob.glob("gh-pages/versions/*"):
    if version.find("devel") == -1:
        version = version.split("/")[-1]
        vs[version] = f"/versions/{version}/"

# remove / deduplicate files into symlinks

keys = list(vs.keys())
keys.sort()

for i in range(len(keys)-1, -1, -1):
    versions.append([keys[i], vs[keys[i]]])

print(f"Saving paths to versions\n{versions}")

with open("gh-pages/versions.json", "w") as FILE:
    json.dump(versions, FILE)
