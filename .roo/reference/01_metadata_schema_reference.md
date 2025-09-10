# Reference: Metadata Schema

This document provides a reference for the metadata schemas used in the project's knowledge base.

### User Story Schema

```markdown
type:: [[story]]
status:: One of: [[TODO]], [[DOING]], [[DONE]]
priority:: One of: [[high]], [[medium]], [[low]]
assignee:: [@username]
epic:: [[EPIC-NAME]]
related-reqs:: [[REQ-ID-1]], [[REQ-ID-2]]
```

### Requirement Schema

```markdown
type:: [[requirement]]
status:: One of: [[PLANNED]], [[IMPLEMENTED]], [[PARTIAL]]
```

### Implementation Plan Schema

```markdown
type:: [[implementation-plan]]
phase:: [[Phase-X]]
related-epics:: [[EPIC-NAME-1]], [[EPIC-NAME-2]]
status:: One of: [[DRAFT]], [[APPROVED]], [[COMPLETED]]
```

### Learning Schema

```markdown
type:: [[learning]]
phase:: [[Phase-X]]
impact:: [[positive]] or [[negative]]
related-stories:: [[STORY-ID-1]], [[STORY-ID-2]]
category:: [[technical]], [[process]], or [[communication]]