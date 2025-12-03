#!/usr/bin/env node
/**
 * OhMyClaude Skill Activation Hook
 *
 * This hook runs on UserPromptSubmit to detect relevant skills based on:
 * - Keyword matching (supports Chinese and English)
 * - Intent pattern matching (regex)
 *
 * Based on: claude-code-infrastructure-showcase
 * Adapted for: OhMyClaude bilingual support
 */

import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

interface HookInput {
    session_id: string;
    transcript_path: string;
    cwd: string;
    permission_mode: string;
    prompt: string;
}

interface PromptTriggers {
    keywords?: string[];
    intentPatterns?: string[];
}

interface SkillRule {
    type: 'guardrail' | 'domain';
    enforcement: 'block' | 'suggest' | 'warn';
    priority: 'critical' | 'high' | 'medium' | 'low';
    description?: string;
    promptTriggers?: PromptTriggers;
    warnMessage?: string;
    blockMessage?: string;
}

interface SkillRules {
    version: string;
    skills: Record<string, SkillRule>;
}

interface MatchedSkill {
    name: string;
    matchType: 'keyword' | 'intent';
    config: SkillRule;
}

async function main() {
    try {
        // Read input from stdin
        const input = readFileSync(0, 'utf-8');
        const data: HookInput = JSON.parse(input);
        const prompt = data.prompt.toLowerCase();

        // Try multiple locations for skill-rules.json
        const possiblePaths = [
            join(process.env.CLAUDE_PROJECT_DIR || data.cwd, '.claude', 'skills', 'skill-rules.json'),
            join(process.env.HOME || '', '.claude', 'skills', 'skill-rules.json'),
        ];

        let rulesPath: string | null = null;
        for (const path of possiblePaths) {
            if (existsSync(path)) {
                rulesPath = path;
                break;
            }
        }

        if (!rulesPath) {
            // No skill rules found, exit silently
            process.exit(0);
        }

        const rules: SkillRules = JSON.parse(readFileSync(rulesPath, 'utf-8'));
        const matchedSkills: MatchedSkill[] = [];

        // Check each skill for matches
        for (const [skillName, config] of Object.entries(rules.skills)) {
            const triggers = config.promptTriggers;
            if (!triggers) {
                continue;
            }

            // Keyword matching (case-insensitive)
            if (triggers.keywords) {
                const keywordMatch = triggers.keywords.some(kw =>
                    prompt.includes(kw.toLowerCase())
                );
                if (keywordMatch) {
                    matchedSkills.push({ name: skillName, matchType: 'keyword', config });
                    continue;
                }
            }

            // Intent pattern matching (regex)
            if (triggers.intentPatterns) {
                const intentMatch = triggers.intentPatterns.some(pattern => {
                    try {
                        const regex = new RegExp(pattern, 'i');
                        return regex.test(prompt);
                    } catch {
                        return false;
                    }
                });
                if (intentMatch) {
                    matchedSkills.push({ name: skillName, matchType: 'intent', config });
                }
            }
        }

        // Generate output if matches found
        if (matchedSkills.length > 0) {
            let output = '';
            output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
            output += '🎯 SKILL ACTIVATION CHECK / 技能激活检测\n';
            output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';

            // Group by priority
            const critical = matchedSkills.filter(s => s.config.priority === 'critical');
            const high = matchedSkills.filter(s => s.config.priority === 'high');
            const medium = matchedSkills.filter(s => s.config.priority === 'medium');
            const low = matchedSkills.filter(s => s.config.priority === 'low');

            if (critical.length > 0) {
                output += '⚠️ CRITICAL / 关键技能 (REQUIRED):\n';
                critical.forEach(s => {
                    const desc = s.config.description || '';
                    output += `  → ${s.name}${desc ? ` - ${desc}` : ''}\n`;
                });
                output += '\n';
            }

            if (high.length > 0) {
                output += '📚 RECOMMENDED / 推荐技能:\n';
                high.forEach(s => {
                    const desc = s.config.description || '';
                    output += `  → ${s.name}${desc ? ` - ${desc}` : ''}\n`;
                });
                output += '\n';
            }

            if (medium.length > 0) {
                output += '💡 SUGGESTED / 建议技能:\n';
                medium.forEach(s => {
                    const desc = s.config.description || '';
                    output += `  → ${s.name}${desc ? ` - ${desc}` : ''}\n`;
                });
                output += '\n';
            }

            if (low.length > 0) {
                output += '📌 OPTIONAL / 可选技能:\n';
                low.forEach(s => {
                    const desc = s.config.description || '';
                    output += `  → ${s.name}${desc ? ` - ${desc}` : ''}\n`;
                });
                output += '\n';
            }

            // Check for warnings
            const warnings = matchedSkills.filter(s => s.config.enforcement === 'warn' && s.config.warnMessage);
            if (warnings.length > 0) {
                output += '⚠️ WARNINGS / 警告:\n';
                warnings.forEach(s => {
                    output += `  ${s.config.warnMessage}\n`;
                });
                output += '\n';
            }

            output += 'ACTION: Use Skill tool BEFORE responding\n';
            output += '操作: 在回复前使用 Skill 工具加载相关技能\n';
            output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';

            console.log(output);
        }

        process.exit(0);
    } catch (err) {
        // Silent failure - don't interrupt user workflow
        process.exit(0);
    }
}

main().catch(() => process.exit(0));
