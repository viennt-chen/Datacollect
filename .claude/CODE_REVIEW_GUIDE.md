# Code Review Guide

Comprehensive review standards for both local reviews and automated CI reviews.

## Core Review Rules

Review using CLAUDE.md for project conventions. Be LEAN and ACTIONABLE — only provide value, avoid noise.

- ONLY include sections when there are ACTUAL issues to report
- NO "Strengths" or praise sections
- NO "no concerns" statements (skip the section entirely)
- NO design/UI/spacing suggestions — you cannot see the visual design
- Reference specific file:line locations for issues
- **If no issues found**:
  - Comment ONLY: `✅ **Approved** - No issues found`
  - DO NOT describe what the changes do
  - DO NOT list changes made
  - DO NOT provide any summary or explanation
  - Zero noise, zero fluff

## Review Sections

Include ONLY if issues exist:

### Bugs/Issues
Logic errors, potential bugs that need fixing

### Best Practices
Violations of language/framework conventions or CLAUDE.md guidelines

### Performance
Actual performance problems (not theoretical)

### Security
Real security vulnerabilities

## Summary Format

End with ONE sentence only with status emoji:
- ✅ **Approved** - [brief reason]
- ⚠️ **Minor Issues** - [what needs fixing]
- 🚨 **Major Issues** - [critical problems]

## Analysis Checklist

Before suggesting removal of "unused" code:
- [ ] Searched ALL usages in the file
- [ ] Checked for dual access patterns
- [ ] Understood purpose of each flag/parameter
- [ ] Verified it's not used by multiple consumers

If unsure, ask: "Was removing [element] intentional?"
