import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MutationReviewer",
    version="0.0.1",
    author="Claudia Chu",
    author_email="cchu@broadinstitute.org",
    description="A tool to review mutations using AnnoMate dashboards",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/getzlab/MutationReviewer",
    project_urls={
        "Bug Tracker": "https://github.com/getzlab/MutationReviewer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires = [
        'AnnoMate>=0.0.2',
        'firecloud-dalmatian',
        'dash-bio'
    ]
)   
