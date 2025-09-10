title:: Log Analysis Protocol Documentation
---
# Log Analysis Protocol

This document describes the mandatory log analysis protocol that must be followed for all development script executions in the project. It provides guidelines, implementation patterns, and best practices for capturing, analyzing, and acting on script execution logs.

## 🎯 Purpose

The log analysis protocol ensures that all script executions are properly monitored, analyzed, and validated. This helps maintain quality, catch issues early, and provide actionable insights from automated processes.

## 📋 Protocol Requirements

According to [`rules.02-scripts_structure`](rules.02-scripts_structure.md), after running any script or terminal command:

1. **Capture Logs**: Always capture both `stdout` and `stderr` logs
2. **Analyze Outcomes**: Summarize key outcomes including successes, failures, and warnings
3. **Take Action**: If errors or warnings are present, decide on next steps
4. **Document Results**: Maintain records of script execution and analysis results

## 🛠️ Implementation Patterns

### Using the Log Analyzer Script

The primary tool for log analysis is the [`log_analyzer.py`](log_analyzer.py) script, which provides comprehensive analysis capabilities:

```bash
# Analyze an existing log file
python scripts/development/log_analyzer.py --log-file script.log

# Execute a command and analyze its output
python scripts/development/log_analyzer.py --command "python my_script.py"

# Execute a command, save output to file, and analyze
python scripts/development/log_analyzer.py --command "python my_script.py" --output script.log
```

### Integration with Existing Scripts

Existing scripts should follow these patterns for proper log analysis integration:

1. **Use Standard Logging**: Utilize the project's logging utilities from [`utils.py`](utils.py)
2. **Structured Output**: Format log messages with clear indicators for different levels
3. **Execution Summaries**: Include start/end timestamps and execution status
4. **Error Handling**: Properly catch and log exceptions with context

Example integration pattern:
```python
from scripts.development.utils import setup_logging, get_logger, log_execution_summary
from datetime import datetime

def main():
    start_time = datetime.now()
    
    # Setup logging
    setup_logging(level="INFO")
    logger = get_logger(__name__)
    
    try:
        # Script logic here
        logger.info("Starting script execution")
        
        # Your code here
        
        logger.info("Script completed successfully")
        success = True
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        success = False
    finally:
        end_time = datetime.now()
        log_execution_summary(start_time, end_time, success=success, logger=logger)
```

## 📊 Log Analysis Categories

The log analyzer categorizes messages into four types:

### Errors
- Critical failures that prevent script completion
- Exceptions and tracebacks
- Missing files or resources
- Configuration issues

### Warnings
- Non-critical issues that should be reviewed
- Deprecated functionality
- Performance concerns
- Potential problems

### Successes
- Confirmation of completed operations
- Positive validation results
- Successful file operations
- Task completions

### Info
- General progress information
- Status updates
- Debug information (in verbose mode)
- Contextual details

## 🤖 Automated Decision Making

Based on log analysis results, the system can automatically determine next steps:

1. **No Errors/Warnings**: Proceed with confidence
2. **Warnings Only**: Review warnings and decide if action is needed
3. **Errors Present**: Halt execution and address issues

## 🧪 Testing and Validation

To test the log analysis protocol:

1. **Create Test Scripts**: Develop scripts that generate various log outputs
2. **Execute with Analysis**: Run scripts through the log analyzer
3. **Verify Categorization**: Confirm messages are properly categorized
4. **Check Recommendations**: Validate that appropriate next steps are suggested

## 🔧 Best Practices

### For Script Developers
- Use consistent log message formats
- Include context in error messages
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Always log script start and completion

### For Log Analysis
- Regular expressions should be specific to avoid false positives
- Consider internationalization in log message detection
- Maintain a balance between sensitivity and accuracy
- Update patterns as new script types are added

### For Integration
- Follow the existing script template patterns
- Use the shared utility functions
- Document script usage and expected outputs
- Include examples in docstrings

## 📈 Monitoring and Reporting

The log analysis protocol enables:

- **Quality Assurance**: Early detection of script issues
- **Performance Monitoring**: Tracking execution times and resource usage
- **Audit Trail**: Complete record of script executions
- **Continuous Improvement**: Data-driven optimization of scripts

## 🔄 CI/CD Integration

In continuous integration pipelines:

```yaml
- name: Run validation script
  run: |
    python scripts/development/validate_kb.py > validation.log 2>&1
    python scripts/development/log_analyzer.py --log-file validation.log
```

This ensures that all automated script executions are properly monitored and validated.

## 📚 Related Documentation

- [`rules.02-scripts_structure`](rules.02-scripts_structure.md) - Script structure guidelines
- [`utils.py`](utils.py) - Shared utility functions
- [`log_analyzer.py`](log_analyzer.py) - Log analysis implementation
- [`STORY-DEV-6`](STORY-DEV-6.md) - User story for this implementation