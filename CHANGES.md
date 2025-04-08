# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- requirements.txt
- restartoai django project
- core django app
- home django app
- core/templates/core/
- core base.html template
- home/templates/home
- home home.html template
- home.urls.py

### Changed

- moved content of django project restartoai/ directory to parent directory
- home.views.py to include home_view()
- restartoai.urls.py to include home urls

### Deleted

- deleted empty restartoai/ project directory after moving contents to parent
- core/models.py
- core/views.py
- core/tests.py
- home/models.py
- home/tests.py