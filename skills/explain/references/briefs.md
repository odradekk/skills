# Briefs for explorers and the explainer

Fill in the placeholders and give each sub-agent only its brief: no conversation history.

## Explorer

> Other explorers are investigating other angles of the same subject at the same time. Cover your angle in depth and leave the rest to them.
>
> **Subject:** {SUBJECT}
> **Your angle:** {ANGLE}
> **Learning goals the explanation serves:** {GOALS}
> **Constraints:** {CONSTRAINTS, such as "read-only: create, edit, or commit nothing" and "the working tree has uncommitted changes that are not part of the subject"}
>
> Read the code, the documents, the decision notes, and the git history that your angle needs. Report:
>
> - **Components:** each type, function, module, or service that matters, with its path and one sentence on what it does.
> - **Flow:** the steps in order: what runs, in which file, what it does, and what it passes to the next step.
> - **Excerpts:** the few short passages the explanation should quote, verbatim, each with its path and line range.
> - **Files read:** every file you read, so the explainer can cite them.
> - **Boundaries:** where this part meets the rest of the system, as its inputs and outputs.
> - **Non-obvious things:** behavior that surprises, history that explains a choice, places where it is easy to get wrong.
> - **Open questions:** what you could not trace or confirm. Say so plainly rather than guessing.

## Explainer

> Write an explanation of {SUBJECT} for {READER}, who should afterwards be able to: {GOALS}.
>
> **Constraints:** {CONSTRAINTS}
>
> {EXPLORER_REPORTS, or "No explorers ran: explore the subject yourself first."}
>
> The reports overlap in places and may disagree. Merge the overlaps, settle disagreements by reading the code yourself, and keep their open questions visible. Cover what the explain skill's table lists for this kind of subject, organized as one section per learning goal, with anything that serves no single goal in one short closing section. Quote excerpts verbatim with their paths. Mark where a figure belongs and what it should show.
>
> Write in {LANGUAGE}, following the plain-language skill at {PLAIN_LANGUAGE_PATH} and its reference for that language: concrete terms, the function and file that do the work instead of roles in the abstract, established terms instead of invented ones, and no narration of how you found things. When something is complex, say why it is complex.
>
> Return the main point in one sentence, the sections, the figure notes, and the sources.
