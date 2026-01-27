---
name: contract-review
description: Representing the client's interests to review, analyze, and revise agreements/contracts. Strictly follows a 7-step workflow: Risk Analysis, Gap Analysis, Comprehensive Proofreading, Legal Opinion Letter, User Confirmation, Automated Revision (Track Changes), and Key Modification Summary.
triggers:
  - 审核协议
  - 审核合同
  - 合同审核
  - Review Agreement
  - Audit Contract
---

# Contract Review Skill

## Overview
## Overview
This skill acts as a dedicated legal counsel representing the **client's interests**. It strictly follows a **7-step workflow** to identify risks, propose improvements, correct errors, generate a formal legal opinion letter, **confirm with the user**, generate a revised document with track changes, and provide a modification summary.

## Critical Instructions
**Whenever the user mentions "审核协议" (Review Agreement), "审核合同" (Audit Contract), or similar terms, YOU MUST EXECUTE THE FOLLOWING 7 STEPS IN ORDER:**

### Step 1: Risk Analysis (风险分析)
Analyze the contract for risks detrimental to the client.
**Sorting Requirement**: Must sort risks from **High** to **Low** severity.

**Categories:**
1.  **核心风险 (Critical Risk - 🔴)**: Severe legal violations, unenforceable terms, major liability traps, fundamental unfairness.
2.  **中等风险 (Medium Risk - 🟡)**: Ambiguities, unfavorable terms, weak protections.
3.  **低级风险 (Low Risk - 🟢)**: Minor issues, optimization suggestions.

**Output Format for Each Item:**
-   **Risk Level**: [Core/Medium/Low]
-   **Location**: [Clause Number/Location]
-   **Risk Description**: [Specific problem]
-   **Reason for Revision**: [Why it hurts the client/Legal basis]
-   **Specific Revision**: [Exact wording to replace the original]

### Step 2: Gap Analysis (缺失条款分析)
Identify clauses that are *missing* but necessary to protect the client's interests.
**Sorting Requirement**: Must sort by **Importance** (High -> Low).

**Output Format for Each Item:**
-   **Importance**: [High/Medium/Low]
-   **Missing Clause**: [Name of the clause]
-   **Defect Analysis**: [How the absence hurts the client]
-   **Specific Addition**: [Complete, specific, and clear wording of the new clause]
-   **Suggested Location**: [Where to insert it]

### Step 3: Comprehensive Proofreading (全面校对)
Check the entire agreement for quality issues in the following categories:
1.  **错别字 (Typos)**
2.  **逻辑 (Logic)**
3.  **格式 (Format)**
4.  **标点符号 (Punctuation)**
5.  **行文 (Writing Style)**
6.  **序号 (Numbering)**

**Output Format:**
-   **Issue Type**: [Category]
-   **Location**: [Specific Clause]
-   **Problem**: [Description]
-   **Modification**: [Corrected Text]

### Step 4: Legal Review Opinion (法律审核意见书)
**Action**: Generate a formal Legal Review Opinion Letter in **Markdown** format.
**Location**: Save in the **SAME DIRECTORY** as the original contract.
**Filename**: `[Original_Filename]_legal_opinion.md`

**Content Template:**
```markdown
# 法律审核意见书

## 一、 审核概况
[Summary of the contract and review scope]

## 二、 核心风险及修改建议 (按风险等级排序)
...

## 三、 缺失条款及完善建议 (按重要度排序)
...

## 四、 全面校对记录
...

## 五、 结论
[Final conclusion and recommendation]
```

### Step 5: User Confirmation (用户确认)
**Action**: **PAUSE** execution.
**Instruction**: Present the "Legal Review Opinion" (Step 4) to the user. Ask for confirmation to proceed with generating the revised contract document.
**Trigger**: Wait for user to say "Proceed", "Confirm", "Generate Revision" or similar.

### Step 6: Automated Revision (修订模式修订)
**Action**: Automatically apply the modifications to the original contract file.
**Method**: Use the `revise_contract.py` script to generate a **Track Changes** version.

**Filename Convention**: 
-   Format: `[Original_Basename]-ABL-[YYYYMMDD].docx`
-   Example: If original is `Contract.docx` and today is 2026-01-19, output is `Contract-ABL-20260119.docx`.

**Command:**
```bash
python3 ~/.gemini/antigravity/skills/contract-review/scripts/revise_contract.py \
  "[Original_File_Path]" \
  --revisions "[Original Text]"|"[New Text]";;"[Original Text 2]"|"[New Text 2]" \
  --output "[Original_Directory]/[Original_Basename]-ABL-[YYYYMMDD].docx" \
  --open
```
*(Note: The `--open` flag will automatically open the file for the user to inspect.)*

### Step 7: Key Modification Summary (修改重点总结)
**Action**: Generate a concise summary of the *key* modifications made to the contract.
**Purpose**: For the client to quickly understand the major changes.
**Filter**: Include only High/Medium risks and critical missing clauses. Exclude typos, formatting, or minor wording tweaks.

**Output Format:**
```text
(In Chat)
合同主要做了如下修改：
1、[Critical Change 1]
2、[Critical Change 2]
...
```

## Usage Examples

**Example User Input:**
> "帮我审核这份《股权转让协议》"

**Agent Execution:**
1.  **Analyze** the document (Steps 1-3).
2.  **Generate Opinion** (Step 4: `股权转让协议_legal_opinion.md`).
3.  **Ask User**: "I have created the review opinion. Shall I generate the revised contract?"
4.  **User Confirms**: "Yes".
5.  **Execute Revision** (Step 6: Run `revise_contract.py` -> Creates & Opens `股权转让协议-ABL-20260119.docx`).
6.  **Final Summary** (Step 7): "合同主要做了如下修改：..."
