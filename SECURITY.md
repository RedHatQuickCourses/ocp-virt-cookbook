# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, send a report to the project maintainers by emailing the repository owner or using [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) feature on this repository.

Include the following in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

## Response Timeline

- **Acknowledgment**: Within 5 business days of receipt
- **Assessment**: Within 10 business days
- **Resolution**: Depends on severity and complexity

## Scope

This project is a documentation site built with Antora. Security concerns most likely involve:

- Credentials or secrets accidentally committed to the repository
- Insecure commands or configurations recommended in tutorials
- Vulnerable dependencies in the build toolchain

## Supported Versions

| Version | Supported |
|---------|-----------|
| main branch (latest) | Yes |
| Older branches | No |

## Best Practices for Contributors

- Never commit secrets, tokens, passwords, or credentials
- Use placeholder values (e.g., `<your-token>`) in tutorials that require credentials
- Do not include kubeconfig files, `.env` files, or private keys
- Review the [CONTRIBUTING.md](CONTRIBUTING.md) guide for content standards
