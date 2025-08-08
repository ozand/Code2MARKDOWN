# API Documentation

## Memory Bank API

### MemoryBank Class
Manages persistent memory for the RooCode agent.

#### Methods

##### store(key, value)
Store a memory entry.

**Parameters:**
- `key` (str): Memory key
- `value` (any): Value to store

**Returns:**
- None

##### retrieve(key)
Retrieve a memory entry.

**Parameters:**
- `key` (str): Memory key

**Returns:**
- Stored value or None

## Specstory API

### Story Class
Represents a user story.

#### Methods

##### add_criteria(criteria)
Add acceptance criteria to the story.

**Parameters:**
- `criteria` (str): Acceptance criteria

**Returns:**
- None

### SpecstoryAgent Class
Manages user stories and requirements.

#### Methods

##### create_story(title, description, priority)
Create a new user story.

**Parameters:**
- `title` (str): Story title
- `description` (str): Story description  
- `priority` (str): Priority level

**Returns:**
- Story object
