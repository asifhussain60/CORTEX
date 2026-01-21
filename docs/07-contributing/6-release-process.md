# Release Process

**Status:** Production Ready | **Last Updated:** 2026-01-21

CORTEX release procedures and checklist.

## Release Phases

### 1. Preparation
- [ ] Merge all PRs for release
- [ ] Update VERSION file
- [ ] Update CHANGELOG.md
- [ ] Create release branch

### 2. Testing
- [ ] Run full test suite
- [ ] Run integration tests
- [ ] Performance benchmarks
- [ ] Security scanning

### 3. Build
- [ ] Build Python package
- [ ] Build Docker image
- [ ] Tag version in Git
- [ ] Create release notes

### 4. Publication
- [ ] Publish to PyPI
- [ ] Push Docker image to registry
- [ ] Create GitHub release
- [ ] Update documentation

### 5. Announcement
- [ ] Update website
- [ ] Send notification to community
- [ ] Post on social media

## Version Numbering

CORTEX uses semantic versioning: MAJOR.MINOR.PATCH

- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

## Related Resources

- [Contributing Guidelines](1-contributing-guidelines.md)
- [Development Setup](../04-guides/deployment/2-development-setup.md)
