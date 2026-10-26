---
name: design-ui
description: 'Design how a screen, flow, or navigation works for the person using it: one focus per view, short paths to the main tasks, every state, and every device and input it must serve, then check the built interface against that design. Use when work adds or changes a user interface, and when the user asks to make an interface easier to use.'
---

# Design UI

The person using an interface has no attention to spare. Every element on a screen competes for it, a screen that shows everything shows nothing, and a user who cannot find what they came for within half a minute gives up. This skill designs how an interface works for that person: what each view is for, how its layout makes its structure plain, how few steps reach the tasks that matter, what the user sees in every state, and whether it holds up on every device and input it must serve. How it looks, its colors, type, and decoration, belongs to the project's design system and its designers.

It has two parts: steps 1 to 6 design the interface before its code, and step 7 checks the interface once it is built. The interface a program offers to other code belongs to the `design-interface` skill, and the logic behind the screens to the `tdd` skill.

The skill runs without stopping for anyone, so that it can be one step of a longer workflow. It decides what the intent leaves open by preferring, in this order, the interface's existing behavior, the convention of the platform and of the rest of the project, and the smaller change, and records each such choice as an assumption. It writes no decision note. A change to the navigation structure, such as moving a section, or what the main menu holds, or removing something users reach today, is hard to reverse for users who learned the old place: unless an accepted note settles it, it is an open decision for planning, and the design keeps the current structure meanwhile.

## 1. Ground the design

- **The intent:** the ticket, the decision note, or the request, and the accepted notes and design documents that touch the interface.
- **The users and their tasks:** who uses this interface, what they come to do, and how often, from the intent, the project's documents, and the interface as it is. List the main tasks, most frequent first.
- **The devices and inputs:** the window sizes, input methods (pointer, touch, keyboard, game controller), languages, and conditions, such as slow networks, that the project says the interface serves. When it does not say, assume the size it is built for now, one narrower and one wider, keyboard-only use, and 200% zoom, and record that as an assumption.
- **The parts the project already has:** its components, its design tokens for spacing, sizes, colors, and type, its icon set, and how it already shows loading, feedback, and errors. Read the interface's directory `AGENTS.md` and the project's design documents for its rules.

Done when you have the main tasks with their frequency, the devices and inputs, and the project's parts and rules.

## 2. Lay out the paths to the tasks

Write each main task as the steps a user takes, from where they start to where it is done, with the label or icon they follow at each step.

- The most frequent tasks take one step from where users start, plus a confirmation when step 5 requires one.
- No task takes more than three steps, and nesting goes no deeper than three levels. A path is short enough only when, at every step, the label or icon makes the next move obvious: users go on through steps they are sure of, and give up at the first one they have to guess.
- What only some users need sits one step away, behind a control that says what it opens, rather than on every screen. Search or a shortcut reaches what no path can keep short.

Done when every main task has its path, every path meets these rules, and every step names what the user follows.

## 3. Give each view one focus

For each view, name the one thing it is for and the one action a user most likely takes there. That task and its action get the weight: the most prominent position, size, and contrast. Everything else in the view is ranked below it, and what serves no task on the view leaves it. The view where users start also shows what waits on them, such as an alert, a failed device, a finished job, or an available update, each with its action or a way to it, below the focus: a count on an icon alone hides what it counts.

Let the layout carry the structure. Group what belongs together by proximity and alignment, separate groups with space, keep the order the same wherever the same things appear, and remove headings and descriptions that only repeat what the grouping already shows. Keep a heading where it names what a group does that its contents do not make plain.

Done when every view has its focus and its primary action written down, every element of it serves a task, and the view where users start shows everything that waits on them.

## 4. Choose the controls and their labels

- **Icons:** an icon alone is faster than a word only when its meaning is conventional, such as search, close, or settings, or when users meet it often. Otherwise pair the icon with a word. A control that leaves the current page, and an action that cannot be undone, keeps its words. Every control shown as an icon alone has a tooltip and a name that screen readers announce. One icon means one thing across the whole interface, and comes from the project's icon set.
- **Labels:** words name what happens, in the user's terms, briefly, by the principles of the `plain-language` skill. Every form field has a label, visible or announced; placeholder text is an example, not a label.
- **Consistency:** the same thing looks and behaves the same everywhere, follows the platform's conventions, and shows the user its choices instead of asking them to remember one.
- **Targets:** every control can be reached by keyboard, in the order of the layout, with its focus visible, and is large enough to hit: at least 24 by 24 CSS pixels, and 44 by 44 where touch is an input.

Done when every control has its form, its label or name, and its keyboard path.

## 5. Design every state

For each view, design what the user sees and can do in each state that can occur, not only the populated one: first use, empty, loading, partly loaded, too much data, failed, and offline when the interface can be.

- **Feedback:** every action answers at once. Use the project's one way of showing each kind of feedback, and choose where it appears by how long it stays relevant: an outcome of one operation goes to a notice that outlives the surface that triggered it, and a state of the view itself, such as a failed load with its retry, stays in the view.
- **Failure:** a failed operation leaves the data the user had on screen. The message sits next to its cause and says how to fix it.
- **Errors prevented:** an action that can be undone offers undo instead of asking for confirmation. An action that cannot be undone, or whose consequence can come before the user could undo it, such as unlocking a door, disarming an alarm, sending a message, or paying, asks first, and its consequence is in the question.
- **Attention kept:** nothing opens or moves that the user did not ask for. Content does not shift under the pointer as it loads, the user's place, such as scroll position, typed input, and selection, survives navigation and refresh, and focus follows the user's action. Motion has a purpose, and respects the system setting for reduced motion.

Done when every view has every state it can reach designed, with its feedback.

## 6. Build it from the project's parts and write the UI contract

Plan the interface from the project's parts: extend an existing component, through a new variant or property, before adding a new one, and add a component only when the same need appears in more than one place or none fits. Spacing, sizes, colors, and type come from the design tokens, and layout follows the content and the container, through the platform's flexible layout and relative units, so that it holds when text grows or the window changes. A value with no token becomes a token, or a named constant beside the component with the reason, never a number repeated in place.

When space runs short on a device in the matrix, in this order: give space to what matters or let elements wrap onto another line; then truncate text, keeping the whole text reachable; then reduce a control to an icon, by the rules in step 4; then move it into a menu. A primary action or state never leaves the view, and nothing shrinks all text or all targets to fit.

Then write the **UI contract**, which the `tdd` skill and step 7 work from: the main tasks with their paths, each view's focus and primary action, the controls and their labels, the states with their feedback, the device matrix, and the components and tokens to use or add. Behavior a test can check, such as what an action does, which state follows a failure, or that a control has its name, goes to `tdd` as cases; the rest are manual checks for step 7.

Done when the contract covers every view, task, state, and device, with the assumptions and open decisions beside it.

## 7. Check the built interface

Once the interface is built, check it against the contract:

- **Paths:** carry out each main task in the running interface, counting the steps, and compare each with its planned path.
- **Focus:** for each changed view, take a screenshot and, when your tools can start a sub-agent, give only the screenshot to a fresh one, with this question: what is this view for, and what would you do first? When the answer misses the view's focus or primary action, the layout does not carry it. Without sub-agents, answer it yourself from the screenshot, and say so in the report.
- **Devices and inputs:** open each changed view at every size and with every input in the matrix, at 200% zoom, and with the longest text the interface can hold, such as a long name or a translation. Nothing overlaps, is cut off without a way to read it, or disappears, and the primary action stays in view.
- **Keyboard:** complete each main task with the keyboard alone; focus stays visible and follows the layout.
- **States:** bring each view into each designed state, such as by emptying its data, slowing the network, or making a request fail, and look at what it shows.
- **Parts:** search the changed interface code for raw sizes, spacing, and colors outside the design tokens, and for controls shown as an icon alone without a name.

A failed check goes back to the step that owns it; fix the interface, by the rules for a test in the `tdd` skill where logic changes, and check again. A check you cannot make, such as one that needs a device or a browser you do not have, is listed as not checked, with what to look at.

Done when every check has passed, or is in the report as not checked with what to look at.

## 8. Report

Report the main tasks with their paths and step counts, each view's focus, the device matrix, the components and tokens used or added, the assumptions, the open decisions, and the results of step 7, including what was not checked.

When another skill called this one, return the report to it. Otherwise write it in the conversation's language, by the principles of the `plain-language` skill.

Done when the report covers every task, view, and check.
