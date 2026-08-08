from setuptools import find_packages, setup


setup(
    name="free-ai-job-search",
    version="0.1.0",
    description="Local-first job-search orchestration with OmniRoute model routing and fallbacks",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.10",
    extras_require={"dev": ["pytest>=8.0"]},
    entry_points={"console_scripts": ["free-job-search=free_job_search.cli:main"]},
)
