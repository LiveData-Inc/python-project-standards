# AI Development Tracking System

This `.ai/` folder implements a comprehensive tracking system for AI-assisted development work.

## 🚀 Initial Setup Instructions for AI Assistants

**CRITICAL INSTRUCTION: Task files are ONLY created when the user explicitly requests with "Task:" prefix in their prompt. DO NOT create task files automatically or proactively.**

**If you are an AI assistant discovering this folder in a project, follow these steps:**

### 1. Check Project Integration
First, verify if the project has been set up for AI tracking:
- [ ] Check if `CLAUDE.md` exists in project root
- [ ] Check if `README.md` mentions the `.ai/` folder
- [ ] Check if `.gitignore` excludes `.ai/` (it should NOT)

### 2. If Not Integrated, Set It Up Now

#### Update or Create `CLAUDE.md` in project root:
```markdown
# [PROJECT NAME] - AI Assistant Instructions

## AI Task Tracking Protocol

**IMPORTANT**: This project uses AI-assisted development tracking.

**Tasks are ONLY created when explicitly requested by the user with "Task:" prefix.**

When a user explicitly requests a task:
1. Create a task file in `.ai/tasks/` with format: `YYYYMMDD-hhmm-description.md`
2. Record the exact user prompt
3. Document all actions taken and files changed
4. Include this task file in the git commit
5. **NEVER modify existing task files** - they are immutable historical records

See `.ai/README.md` for complete task logging protocol.

## Project Context
[Add project-specific context here]
```

#### Update `README.md` to mention AI tracking:
```markdown
## Development

This project uses AI-assisted development tracking. See `.ai/README.md` for details.
```

#### Ensure `.gitignore` does NOT exclude `.ai/`:
```gitignore
# AI tracking should be included in version control
!.ai/
!.ai/**
```

### 3. Start Using the System
Once integrated, ALWAYS create task files for your work.

---

## 📁 Structure

```
.ai/
├── AI_CHANGELOG.md      # High-level summary of all AI work
├── README.md            # This file (system documentation)
└── tasks/               # Individual task logs
    └── TASKS.md
    └── YYYYMMDD-hhmm-description.md
```

## 📝 Task Logging Protocol

### When to Create Task Files
**ONLY create task files when the user explicitly requests with:**
- "Task:" prefix in their prompt
- Explicit instruction to "create a task" or "log this task"

**DO NOT create task files:**
- Automatically based on work being done
- Proactively when you think it's needed
- Unless explicitly instructed by the user

### File Naming Convention
Each AI-assisted task creates a file in `.ai/tasks/` with format:
```
YYYYMMDD-hhmm-description-with-hyphens.md
```

Examples:
- `20250829-1430-setup-react-frontend.md`
- `20250829-1515-add-authentication-system.md`
- `20250830-0900-fix-database-connection.md`

### Task File Template
Each task file MUST contain:

```markdown
# Task: [Brief Description]

## Date
YYYYMMDD-hhmm

## Prompt
[Exact user prompt that initiated this task]

## Context
[Any relevant context about why this task was needed]

## Actions Taken
1. [Step-by-step list of actions]
2. [Include file paths affected]
3. [Note any decisions made]

## Files Changed
- `path/to/file1.ts` - Description of changes
- `path/to/file2.md` - Description of changes

## Testing
[How the changes were tested/verified]

## Outcome
[Result of the task - success, partial, blocked, etc.]

## Notes
[Any additional observations or follow-up needed]
```

## 🎯 AI Interaction Mode

### Critical Review Mode (DEFAULT - RECOMMENDED)
**This template recommends Critical Review Mode as the default interaction style.**

In Critical Review Mode, AI assistants should:
- **Eliminate reflexive compliments** - No automatic praise or validation
- **Provide rigorous, objective feedback** - Focus on technical merit
- **Question assumptions** - Challenge approaches that seem suboptimal
- **Prioritize problems over positivity** - Identify issues, not just solutions
- **Earn praise through merit** - Only acknowledge genuinely exceptional work

**Key principles:**
1. Before complimenting, assess: Is this genuinely insightful? Is the logic exceptionally sound?
2. For standard or underdeveloped work: Analyze, question, suggest improvements
3. Replace "Great idea!" with "This approach has trade-offs..."
4. Replace "Looks good!" with "Consider these edge cases..."

### Supportive Mode (Alternative)
If your project prefers supportive interactions, document this in your project's CLAUDE.md:
- Encouraging and solution-focused
- Explanatory and thorough
- Validates approaches before critiquing

**To switch modes:** Add to your project's CLAUDE.md:
```markdown
## AI Interaction Preference
This project uses SUPPORTIVE mode for AI interactions.
```

## ⚠️ Critical Rules

### For AI Assistants - YOU MUST:
1. **ONLY** create a task file when user explicitly requests with "Task:" prefix
2. **ALWAYS** record the exact user prompt verbatim when creating a task
3. **ALWAYS** list all files modified or created in the task file
4. **NEVER** create task files automatically or proactively
5. **NEVER** modify existing task files (they are historical records)
6. **UPDATE** AI_CHANGELOG.md after significant tasks (when task file exists)

### Task File Immutability
**IMPORTANT**: Task files in `.ai/tasks/` are IMMUTABLE historical records
- Once created, task files must NOT be edited
- If corrections needed, create a new task file referencing the original
- These files serve as permanent audit trail
- Treat them like git commits - they capture a moment in time

## 🔄 Workflow

### Starting a Task
1. User provides a prompt with "Task:" prefix
2. ONLY THEN create file: `.ai/tasks/YYYYMMDD-hhmm-task-description.md`
3. Record the prompt exactly as given
4. Document actions as you perform them
5. List all files as you change them

**If user does not explicitly request a task, proceed with work WITHOUT creating a task file.**

### During the Task
- Update the task file as you work
- Include failed attempts and why they failed
- Document decisions and trade-offs
- Note any blockers or issues

### Completing a Task
1. Finalize the task file with outcomes
2. Update `AI_CHANGELOG.md` with summary (if significant)
3. Ensure task file is complete before moving on
4. Include task file in any git commits

## 🔗 Git Integration

### Commit Messages
When committing code with AI assistance:
```bash
git add .
git commit -m "feat: add user authentication [AI: 20250829-1430]"
```

The `[AI: YYYYMMDD-hhmm]` reference links the commit to the task file.

### Benefits
1. **Traceability**: Every change linked to prompt and reasoning
2. **Knowledge Transfer**: Future AI sessions have complete context
3. **Debugging**: Can trace back why specific decisions were made
4. **Learning**: Review what worked and what didn't
5. **Audit Trail**: Complete record of AI involvement

## 📊 Maintaining AI_CHANGELOG.md

The `AI_CHANGELOG.md` file should track:
- Major milestones completed
- Significant architectural decisions
- Problems solved
- Patterns discovered
- Metrics (files created, tests added, etc.)

Update it after completing significant tasks or at session end.

## 🎯 Project Customization

### For Human Developers
After copying this `.ai/` folder to a new project:

1. Update `AI_CHANGELOG.md` header with project name
2. Clear out any example task files
3. Ensure your AI assistant reads this README
4. Consider adding project-specific guidelines below

### Project-Specific Guidelines
<!-- Add any project-specific AI guidelines here -->
[This section is for project-specific rules and context]

## 🤖 For AI Assistants: Your Checklist

Every time you start work in this project:
- [ ] Read this entire README
- [ ] Check for existing task files to understand project history
- [ ] Verify project integration (CLAUDE.md exists and references this system)
- [ ] Wait for explicit "Task:" prefix before creating task files
- [ ] Follow the protocol WITHOUT exceptions

## 💬 Coaching Your AI Assistant

### Why Reminders Are Important
AI assistants may not automatically discover or follow the `.ai/` folder instructions. You should periodically remind them to check and follow the tracking protocol, especially:
- At the start of a new session
- When switching between major tasks
- If the AI seems to skip documentation
- When working with a different AI assistant

### Example Prompts to Guide Your AI

#### Initial Session Setup
- "Please read the instructions in the `.ai/` folder and follow the tracking protocol for all work"
- "Before starting, review `.ai/README.md` and create appropriate task files"
- "Check the `.ai/` folder for our AI development tracking system and follow it"

#### During Development
- "Task: [specific task to complete and document]"
- "Please update the AI_CHANGELOG.md with this significant change" (if task exists)

#### Review and Compliance
- "Re-read the instructions in `.ai/README.md` and ensure all task files are complete"
- "Review all files in `.ai/` for correctness and update as needed"
- "Check that you've been following the `.ai/` tracking protocol correctly"

#### Specific Corrections
- "You need to create a task file for this work - see `.ai/README.md`"
- "The task file should include the exact prompt I gave you"
- "Remember task files are immutable - don't modify existing ones"

### Signs Your AI Needs a Reminder
- Creating task files without explicit "Task:" prefix
- Creating task files automatically or proactively
- Forgetting to document file modifications in requested task files
- Skipping the prompt recording in task files
- Modifying existing task files
- Not updating AI_CHANGELOG.md for major work (when task exists)

### Best Practices
1. **Start each session** with: "Please check `.ai/README.md` for our tracking protocol"
2. **Use "Task:"** prefix when you want work documented in a task file
3. **Be explicit** about when you want task files created
4. **Reference specific files** like `.ai/README.md` rather than general instructions
5. **Verify compliance** by checking `.ai/tasks/` for new task files only when requested

## 📚 Examples and Patterns

### Good Task File Names
- `20250829-1430-implement-user-authentication.md` ✅
- `20250829-1545-fix-login-bug.md` ✅
- `20250830-0900-refactor-database-queries.md` ✅

### Bad Task File Names
- `update.md` ❌ (no timestamp)
- `20250829-authentication.md` ❌ (missing hhmm)
- `2025-08-29-1430-task.md` ❌ (wrong format - has hyphens in date)
- `20250107-1430-task.md` ❌ (incorrect date - should be 20250907 for September)

## 🔍 Finding Information

To understand project history:
1. Read `AI_CHANGELOG.md` for high-level overview
2. List task files chronologically: `ls -la .ai/tasks/`
3. Search for specific work: `grep -r "authentication" .ai/tasks/`
4. Review recent tasks to understand current state

---

**Remember**: This system creates a permanent record of AI-assisted development. Treat it with the same care as source code.