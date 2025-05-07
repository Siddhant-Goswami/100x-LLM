from setuptools import setup, find_packages

setup(
    name="ai_crm",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.104.0,<0.105.0",
        "uvicorn>=0.23.0,<0.24.0",
        "pydantic>=2.4.0,<2.5.0",
        "email-validator>=2.0.0,<2.1.0",
        "groq>=0.4.0,<0.5.0",
        "python-dotenv>=1.0.0,<1.1.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: FastAPI",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.10",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered CRM system for lead qualification",
    keywords="crm, ai, qualification, leads, fastapi, streamlit",
) 