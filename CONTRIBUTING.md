# Contributing to 4TS

Thank you for your interest in contributing to the Four Tests Standard! This document provides guidelines for contributing to the project.

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background or identity.

### Expected Behavior

- Be respectful and constructive in all interactions
- Focus on what is best for the community and the standard
- Show empathy towards other community members
- Accept constructive criticism gracefully
- Respect differing viewpoints and experiences

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing private information without permission
- Spam or commercial solicitation
- Any conduct that would be inappropriate in a professional setting

## How to Contribute

### Reporting Issues

**Bug Reports:**
- Use the GitHub issue tracker
- Include detailed description of the problem
- Provide steps to reproduce
- Include expected vs actual behavior
- Attach relevant PCDs or test cases (anonymized if necessary)

**Feature Requests:**
- Explain the use case and rationale
- Describe how it aligns with the Four Tests principles
- Consider backward compatibility implications

### Submitting Changes

1. **Fork the Repository**
   ```bash
   git clone https://github.com/ferz-ai/4ts-standard.git
   cd 4ts-standard
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add protocol-replay support for X"
   ```
   
   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

4. **Submit a Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Explain rationale and trade-offs
   - Be responsive to review feedback

### Types of Contributions

#### 1. Specification Improvements

**Clarifications** (non-breaking):
- Improved wording or examples
- Additional diagrams or illustrations
- Expanded FAQ sections

**Extensions** (minor version):
- New optional fields (under must-ignore policy)
- Additional error codes
- New implementation profiles

**Breaking Changes** (major version):
- Changes to PCD schema structure
- Modified verification logic
- Incompatible updates

⚠️ **Note:** Due to CC BY-NC-ND 4.0 licensing, specification changes require approval from FERZ LLC as steward. Open an issue for discussion before investing significant effort.

#### 2. Schema & Tools (MIT Licensed)

**Freely Contribute:**
- New test vectors
- Reference implementation improvements
- Bug fixes in validator
- Language bindings (Python, Go, Rust, etc.)
- Integration examples
- Performance optimizations

#### 3. Documentation

**Always Welcome:**
- Tutorial improvements
- Use case examples
- Integration guides
- Translation to other languages
- Video tutorials (link from docs)

#### 4. Testing

**High Value:**
- Additional conformance test vectors
- Edge case coverage
- Performance benchmarks
- Interoperability tests
- Security audits

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/ferz-ai/4ts-standard.git
cd 4ts-standard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

### Testing Requirements

All contributions must include appropriate tests:

**For Schema Changes:**
- Test vectors demonstrating the change
- Both positive and negative cases
- Backward compatibility tests

**For Tool Changes:**
- Unit tests for new functionality
- Integration tests with existing components
- Performance tests if applicable

**For Documentation:**
- Verify all links work
- Check rendering in Markdown viewers
- Spell check

### Running Tests

```bash
# Run full test suite
pytest tests/

# Run specific test file
pytest tests/test_validator.py

# Run with coverage
pytest --cov=tools --cov-report=html

# Run conformance tests
python tools/validator/quickstart_validate.py --all
```

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `pylint` for linting

```bash
# Format code
black tools/

# Lint code
pylint tools/
```

**Markdown:**
- Use consistent heading hierarchy
- Include blank lines around code blocks
- Use reference-style links for repeated URLs

## Release Process

### Versioning

4TS follows Semantic Versioning (SemVer):

- **MAJOR** (x.0.0): Breaking changes to PCD schema or verification logic
- **MINOR** (1.x.0): New optional features under must-ignore policy
- **PATCH** (1.0.x): Bug fixes, documentation improvements

### Changelog Updates

All user-facing changes must be documented in CHANGELOG.md:

```markdown
## [1.0.3] - 2025-12-01

### Added
- New test vector for Merkle tree verification

### Fixed
- Canonicalization bug with scientific notation

### Changed
- Improved error messages for E_HASH_MISMATCH
```

## Conformance Bundle Maintenance

### Adding Test Vectors

When adding new test vectors to the conformance bundle:

1. **Create the PCD file**
   ```bash
   # Positive case
   touch test-vectors/positive/PCD-A4_description.json
   
   # Negative case
   touch test-vectors/negative/NC-6_description.json
   ```

2. **Document expected behavior**
   - Add entry to ERROR_CATALOG.md (for negative cases)
   - Update README.md test vector count
   - Add test case to quickstart_validate.py

3. **Update manifest**
   ```bash
   python tools/update_manifest.py
   ```

4. **Verify all tests pass**
   ```bash
   python tools/validator/quickstart_validate.py --all
   ```

### Updating Schemas

Schema changes require careful consideration:

1. **Maintain backward compatibility** (for minor versions)
   - Add new optional fields only
   - Do not change existing field types
   - Do not remove fields

2. **Update schema version**
   ```json
   {
     "$schema": "https://json-schema.org/draft/2020-12/schema",
     "$id": "https://github.com/ferz-ai/4ts-standard/schemas/pcd.schema.json",
     "version": "1.0.3"
   }
   ```

3. **Add migration guide** (for major versions)
   - Document all breaking changes
   - Provide migration script
   - Update compatibility matrix

## Community Governance

### Decision Making

**Technical Decisions:**
- Proposals discussed in GitHub issues
- Community feedback period (minimum 2 weeks for breaking changes)
- Final decision by FERZ LLC technical team
- Transparency through public issue tracker

**Process Decisions:**
- Community discussion in GitHub Discussions
- Consensus-based when possible
- Documented in CONTRIBUTING.md updates

### Recognition

Contributors are recognized through:
- GitHub contributor listings
- Credits in release notes
- Mention in CHANGELOG.md for significant contributions
- Optional listing in CONTRIBUTORS.md

## Getting Help

**Questions:**
- GitHub Discussions for general questions
- GitHub Issues for specific problems
- Email contact@ferzconsulting.com for private inquiries

**Resources:**
- [Quick Start Guide](docs/quickstart.md)
- [Implementation Guide](docs/implementation-guide.md)
- [FAQ](docs/faq.md)
- [Specification](SPECIFICATION.md)

## Licensing

By contributing to 4TS, you agree that:

1. **Specification contributions** will be licensed under CC BY-NC-ND 4.0
2. **Schema/code contributions** will be licensed under MIT
3. You have the right to submit the contribution
4. Your contribution does not violate any third-party rights

See [LICENSE.md](LICENSE.md) for complete terms.

## Contact

- **Technical Questions:** GitHub Issues
- **Licensing Questions:** contact@ferzconsulting.com
- **Security Issues:** security@ferzconsulting.com (private disclosure)
- **Partnership Inquiries:** contact@ferzconsulting.com

---

Thank you for contributing to 4TS! Together we're building critical infrastructure for verifiable AI governance.

**© 2025 FERZ LLC**
