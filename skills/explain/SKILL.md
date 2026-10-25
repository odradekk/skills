---
name: explain
description: Explain a change, a part of the codebase, a concept, a decision, or a failure with figures and a short quiz that checks the reader understood; started only by the user.
disable-model-invocation: true
---

# Explain

The aim is understanding, not completeness. Start from what the reader must be able to do afterwards, explain only what that needs, show it with figures, and end with a quiz that tells you both whether it worked.

## 1. Set the target

- **Subject:** a change (a diff, a branch, a pull request, or a range of commits), a part of the codebase, a concept or mechanism, a decision note, or a failure.
- **Reader:** the user, unless the user names someone else. Judge what the reader already knows from the conversation.
- **Learning goals:** two to four things the reader should be able to do afterwards, written as actions: predict what happens when something occurs, find where something is decided, say why one approach was chosen over another. Take them from the request.
- **Size:** a narrow subject, such as one function or a small change, gets an answer in the reply. A subject with several parts gets a page.

When the request leaves the subject or the goals unclear, ask before building. Otherwise go ahead: state the subject and the goals in one or two lines at the top of the reply or the page, and rebuild when the user corrects them.

Done when the subject, reader, goals, and size are set.

## 2. Gather the material

Facts come from the repository and its history, not from memory. Use fresh sub-agents, when your tools can start them, so the exploring stays out of your context: the user started this skill, and the skill asks for them. The explainer is a sub-agent too. Without sub-agents, play each role yourself, in order.

- **Simple subject:** one explainer explores and drafts in one pass.
- **Subject that spans several modules, services, or areas of a change:** split it into two to four angles, such as the data model, the request flow, failure handling, and history. One explorer per angle works in parallel, on a fast model; then one explainer, on the most capable model available, combines their reports.

[references/briefs.md](references/briefs.md) holds the briefs for both roles. What to gather depends on the subject:

| Subject | What the material covers |
|---|---|
| A change | Why it was made (the tickets, the decision note, the pull request description, or without them the commit messages and the diff, saying so when no reason is recorded); what changed, by area; behavior before and after; risks; a reading order through the files |
| A part of the codebase | What it is and why it exists; the key concepts; how it works, step by step; where things live; pitfalls |
| A concept | A plain definition first, then where and how this project uses it |
| A decision note | The problem; the choice; the alternatives and why they lost; the consequences; the code that implements it |
| A failure | What triggered it; what went wrong, step by step; why the fix works; the test that guards it |

Done when every learning goal has material with its sources, such as paths and commits, and the open questions are listed.

## 3. Build the explanation

Lead with the main point in one sentence. Then give one section per learning goal, or per step of a flow, each with a few short paragraphs and at least one figure; a table counts as a figure. Material that the table above asks for but that serves no single goal, such as risks or a reading order, goes into one short closing section. Get the figures from the `visualize` skill, which also builds the page when the size calls for one.

Use short real excerpts with their paths; when no real excerpt shows the point, a made-up example is allowed if it is labeled as one. Write in the reader's language and revise the text with the `plain-language` skill; the quiz takes the place of its new-reader check. Open questions from the exploration go in a clearly marked box rather than out of sight.

## 4. Quiz

Write three to five questions for a page, or one or two in a reply. Each question checks one learning goal:

- **Kinds:** predict the behavior in a situation, find the owner of a decision, explain a trade-off, spot the defect in a short excerpt, or put steps in order.
- **Answerable from the explanation,** but not by matching words: rephrase instead of copying sentences.
- **Wrong options come from real misconceptions:** the behavior before the change, a plausible owner that is not the real one, the alternative that lost.
- **Feedback for every option:** why it is right or wrong, with a link to the section that explains it.

On a page, the first choice on a question locks it and shows that option's feedback; the score appears once every question is answered; and a button copies the answers as plain text, each question with the chosen and the correct option, for the user to paste into the conversation. Make the copy button fall back to a selectable text box when the clipboard is unavailable. In a reply, list the options, wait for the user's answers, then give the feedback.

When the user's answers come back with mistakes, explain each missed goal again in the conversation with a different figure or example, not by repeating the same text.

## 5. Deliver

For a page, write and open it through the `visualize` skill, whose temporary-directory rule applies, and give the user its path with a two-sentence summary: the main point, and what the page covers. For a reply, give the explanation and the quiz.

Done when the reader has the explanation and the quiz.
