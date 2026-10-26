---
name: plain-language
description: 'Revise writing for people so it reads the way an experienced colleague talks: the main point first, nothing redundant, established terms, and no unexplained labels or literal translations. Use when writing or revising documents, notes, tickets, pull request descriptions, commit bodies, or reports, and when the user objects to a wording.'
---

# Plain language

A reader should get the main point on the first reading, follow the reasoning without gaps, meet only words the reader already uses, and find no passage that is redundant or off the point: more text is not better.

Creative writing, such as fiction, game dialogue and scripts, and setting or lore documents, is outside this skill: its wording is part of the content, and it follows the project's own writing guides.

This skill is the revision pass. Write the draft from the principles in [core.md](core.md), then revise it here. Models fall back into the same habits while drafting, so the checking happens after the draft exists.

## Protected text

Leave these exactly as they are:

- code, commands, identifiers, file paths, and configuration keys;
- quotations, quoted output, and error messages;
- lines whose format a tool checks, such as `Status: rejected — <reason>` in a decision note;
- the field's established terms, and the project's own names, such as directory names and in-game text, even when they look unusual to an outsider.

## Whole text

These tests come before the sentence tests: a sentence you are about to cut needs no polishing.

1. **Main point.** Can you state the text's main point in one sentence? Put it first, or answer the reader's question first. If you cannot state it, settle what the point is before revising anything else.
2. **Line of reasoning.** Does every paragraph follow from the main point or from the paragraph before it, so the reader knows why it comes next? Add the missing link, reorder, or move the passage to where it connects. A jump between topics without a stated link is a gap, even when each part is correct.
3. **Relevance.** Does each paragraph, list item, and caveat serve the reader's question or task? Cut what does not, even when it is true or took effort to find.
4. **Repeated content.** Is any point made twice, as in a closing summary of the body, one caveat in several places, or list items that restate each other? Keep it once, where it matters most.
5. **Proportion.** Does space follow importance? The main point and what the reader must act on get the most room; background and caveats stay short.

## Sentences

1. **Coined term.** Did you give this thing its name during the work? Replace the name with a plain description, or with the field's established term.
2. **Borrowed term.** Would a practitioner of this field say this word? A word borrowed from another field, such as law, medicine, or the military, or a metaphor posing as a technical noun, becomes the plain word.
3. **Literal translation.** Is there an established translation? Use it. When practitioners say the original word, keep the original word.
4. **Unseen abbreviation or label.** Has the reader seen the full form? Spell it out, or say what it refers to. Labels from your own working steps, such as "option B", "Q3", or "step 2", mean nothing to a reader who never saw those steps.
5. **Repeated pattern.** Does the same sentence frame or word recur in the text? Keep the one occurrence that does real work and restate the rest plainly.
6. **Empty sentence.** Can you restate it as an instruction, a fact, or a number? Could it appear unchanged in another project's text? Cut a sentence that fails either question.
7. **Hidden actor.** Does the sentence say who does what? Name the actor and use the verb, in place of a passive or a noun such as "perform a validation".
8. **Compressed sentence.** Does the reader have to decode arrows, symbols, or fragments without verbs? Write the full sentence.
9. **Process residue.** Does the text narrate how you got here, such as what you checked first, what something used to be, or what changed in review? State the current result.
10. **Format.** Does each heading, bold phrase, list, or table help this reader find or compare something? Turn the rest into prose.
11. **Spoken test.** Would an experienced colleague say this sentence in a face-to-face conversation? If not, rewrite it the way they would say it.

## Revise

1. Mark the protected text.
2. Read the reference for the draft's language, which lists the patterns that fail these tests most often, each with an example and a rewrite: [references/zh.md](references/zh.md) for Chinese, [references/en.md](references/en.md) for English, both for mixed text.
3. Apply the whole-text tests: settle the main point, then reorder, link, and cut.
4. Apply every sentence test to every remaining sentence and rewrite what fails. A sentence rewrite keeps every claim, number, and condition the sentence carries; content leaves the text only through the whole-text tests.
5. Apply the house style from the `Prose` line of the repository's `## Agent workflow` section, if it has one. House style takes precedence over the defaults in the language references.

Done when the text passes the whole-text tests, every sentence passes every sentence test, the house style is applied, and the protected text is unchanged.

## New-reader check

A decision note, ticket, README, or pull request description is read by people and agents who never saw your work. After revising such a document, give it to a sub-agent that has none of your context, where your tools allow; otherwise, reread it as if you had never seen the work. Give the reader only the text and who it is for, such as "a developer new to this project", and ask for:

- the main point, in one sentence, as the reader understood it;
- every place where it could not tell why a passage comes next, and every passage it found redundant or off the point;
- every word, abbreviation, or reference it could not understand from the text and general knowledge of the field;
- every sentence it had to read twice.

When the reader's main point differs from yours, the main point or the line of reasoning needs work. Fix each listed item, or confirm that it is an established term this reader is expected to know.

Done when the reader's main point matches yours and every listed item is fixed or confirmed.

## Record the user's corrections

When the user objects to a wording, fix it, then record the pattern, the observed example, and the rewrite under its category in the matching language reference, or add the example to the pattern when it is already listed. Make the change in this skill's source repository (https://github.com/odradekk/skills), because a sync replaces installed copies. When you are not working in that repository, give the user the case to add.
