# Skills & Hooks Management Guide

Complete guide to managing, troubleshooting, and fine-tuning the progressive disclosure documentation system.

## Overview

This guide explains how to manage the automated documentation system that suggests relevant skills based on your prompts and file context.

## 🎯 System Components

### 1. Hooks (The Automation Layer)

**What**: Shell scripts that run automatically at specific events
**Where**: `.claude/hooks/`
**Purpose**: Analyze prompts and suggest relevant skills

**The hooks**:
- `skill-activation-prompt.sh` — UserPromptSubmit event
- `post-tool-use-tracker.sh` — PostToolUse event
- `{{formatter}}-post-edit.sh` — PostToolUse event (formatting)

**Configuration**: `skill-rules.json` — Defines keywords and patterns

### 2. Skills (The Documentation Routers)

**What**: Short markdown files (~100-200 lines) that act as "smart routers"
**Where**: `.claude/skills/*/SKILL.md`
**Purpose**: Provide critical rules + quick patterns + point to comprehensive guides

### 3. Specialized Guides (The Deep Knowledge)

**What**: Comprehensive documentation files
**Where**: Various locations in the project
**Purpose**: Single source of truth for deep technical knowledge

## 🔍 Diagnostic Commands

### View Activation Logs
```bash
tail -20 .claude/logs/skill-activations.log
tail -f .claude/logs/skill-activations.log
grep "skill-name" .claude/logs/skill-activations.log
```

### View Current Configuration
```bash
cat .claude/hooks/skill-rules.json | jq .
cat .claude/hooks/skill-rules.json | jq '.skills."skill-name".promptTriggers.keywords'
```

### Test Skill Activation Manually
```bash
echo '{"prompt":"your prompt here"}' | .claude/hooks/skill-activation-prompt.sh
```

### Verify Hook Permissions
```bash
ls -l .claude/hooks/*.sh
# Should show: -rwxr-xr-x
chmod +x .claude/hooks/*.sh
```

## 🛠️ Creating a New Skill

### When to Create

Create when:
- ✅ Distinct domain of knowledge
- ✅ Comprehensive documentation to route to
- ✅ Topic comes up frequently
- ❌ DON'T create for one-off topics

### Steps

1. **Create the specialized guide** (Level 3)
2. **Create the skill** (Level 2): `mkdir -p .claude/skills/my-skill && touch SKILL.md`
3. **Use the smart router template** (~100-200 lines)
4. **Add to skill-rules.json**
5. **Test activation**

## 🚨 Common Issues & Fixes

### Issue: Hook Not Executing
```bash
ls -l .claude/hooks/skill-activation-prompt.sh
chmod +x .claude/hooks/skill-activation-prompt.sh
```

### Issue: Invalid JSON in skill-rules.json
```bash
jq . .claude/hooks/skill-rules.json
```

### Issue: Too Many Skills Suggested
```json
"config": { "maxSkillsPerPrompt": 2 }
```

## ✅ Checklist: System Health

- [ ] All hooks are executable
- [ ] skill-rules.json is valid JSON
- [ ] Logs directory exists
- [ ] Recent activations visible in logs
- [ ] All skills exist and are readable
