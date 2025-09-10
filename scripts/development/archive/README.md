title:: Development Scripts Archive
---
# Development Scripts Archive

This directory contains obsolete development scripts that are no longer actively used but are preserved for historical reference and potential future use.

## 📋 Table of Contents

- [Purpose](#purpose)
- [Organization](#organization)
- [Archival Process](#archival-process)
- [Archive Structure](#archive-structure)
- [Finding Archived Scripts](#finding-archived-scripts)
- [Restoration Process](#restoration-process)
- [Archived Scripts Index](#archived-scripts-index)

## 🎯 Purpose

The archive directory serves several important functions:

1. **Historical Preservation**: Maintains a record of scripts that were once useful
2. **Clean Active Directory**: Keeps the main `scripts/development/` directory focused on actively used tools
3. **Reference Material**: Provides examples and patterns for future script development
4. **Audit Trail**: Documents why scripts were archived and what replaced them

## 📁 Organization

Scripts are organized by year and category to make discovery easier:

```
archive/
├── 2024/
│   ├── migrations/     # Database/data migration scripts
│   ├── utilities/      # General utility scripts
│   └── analysis/       # Analysis and reporting scripts
├── 2023/
│   └── [categories]/   # Same structure for previous years
└── README.md          # This file
```

## 🔄 Archival Process

### When to Archive a Script

A script should be archived when it meets any of these criteria:

1. **One-time Use**: Scripts created for specific, non-repeating tasks
2. **Superseded**: Scripts replaced by newer, better implementations
3. **Broken Beyond Repair**: Scripts that are broken and not worth fixing
4. **Unused**: Scripts that haven't been used in 6+ months
5. **Deprecated**: Scripts that depend on deprecated systems or APIs

### Archival Steps

1. **Create Archive Entry**: Document the script in the index below
2. **Move Script**: Move the script file to appropriate archive directory
3. **Preserve Documentation**: Copy any relevant documentation
4. **Update References**: Update any documentation that references the script
5. **Git Commit**: Commit the archival with clear message

### Archive Entry Template

When archiving a script, use this template for the index:

```markdown
### Script Name (YYYY-MM-DD)
- **Original Location**: `scripts/development/original_script.py`
- **Archive Location**: `scripts/development/archive/2024/utilities/original_script.py`
- **Purpose**: Brief description of what the script did
- **Reason for Archival**: Why it was archived (superseded, one-time use, etc.)
- **Replacement**: What script or process replaced it (if applicable)
- **Key Features**: Notable features or patterns worth preserving
- **Usage Example**: How it was typically used
- **Dependencies**: Any special dependencies or requirements
- **Lessons Learned**: What we learned from this script
```

## 🔍 Finding Archived Scripts

### By Category
Browse the directory structure by year and category to find scripts of interest.

### By Search
Use search tools to find scripts by name or content:
```bash
# Search for specific script name
find scripts/development/archive -name "*script_name*" -type f

# Search for content within scripts
grep -r "specific functionality" scripts/development/archive/
```

### By Index
Check the [Archived Scripts Index](#archived-scripts-index) below for a curated list with descriptions.

## ♻️ Restoration Process

If you need to restore an archived script:

1. **Evaluate Need**: Confirm the script is still relevant
2. **Check Dependencies**: Verify all dependencies are still available
3. **Test Thoroughly**: Test the script in a safe environment
4. **Update Documentation**: Update any outdated documentation
5. **Move Back**: Move the script back to `scripts/development/`
6. **Update Index**: Update this README to reflect the restoration

### Restoration Checklist
- [ ] Script functionality verified
- [ ] Dependencies available and working
- [ ] Documentation updated
- [ ] Integration with current systems tested
- [ ] Archive index updated

## 📚 Archived Scripts Index

### 2024

#### Migrations
*No archived migration scripts yet*

#### Utilities
*No archived utility scripts yet*

#### Analysis
*No archived analysis scripts yet*

### 2023

#### Migrations
*No archived migration scripts yet*

#### Utilities
*No archived utility scripts yet*

#### Analysis
*No archived analysis scripts yet*

## 📝 Adding to the Archive

When archiving a new script:

1. **Choose Appropriate Location**: Select the correct year and category
2. **Create Archive Entry**: Add entry to the index above
3. **Follow Template**: Use the template provided above
4. **Be Thorough**: Include all relevant information for future reference
5. **Maintain Consistency**: Follow the established format and style

## 🔗 Related Documentation

- [`../README.md`](../README.md) - Main development scripts documentation
- [`rules.02-scripts-structure`](rules.02-scripts-structure.md) - Script structure guidelines
- [`STORY-DEV-3`](STORY-DEV-3.md) - User story for script lifecycle management

## 💡 Best Practices

1. **Archive Early**: Don't wait too long to archive unused scripts
2. **Document Thoroughly**: Include comprehensive information about archived scripts
3. **Maintain History**: Preserve the original documentation and comments
4. **Cross-Reference**: Link to related scripts or documentation
5. **Regular Review**: Periodically review the archive for cleanup opportunities

## 📞 Support

For questions about the archive or restoration process:
1. Check this documentation first
2. Review the archived script's original documentation
3. Create a new issue or user story if needed
4. Follow the project's contribution guidelines

---
*This archive is maintained as part of the Code2Markdown project development infrastructure.*