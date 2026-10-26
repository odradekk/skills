# English writing reference

## 1. Structure: redundancy and gaps

Check: state the main point in one sentence, then ask of each paragraph how it relates to the main point or to the paragraph before it, and whether the reader needs it. More text is not better; surplus text buries the point.

| Pattern | Rewrite |
|---|---|
| A warm-up before the answer ("Before getting into this, some background…") | Answer first; keep only the background the answer depends on |
| A closing recap of the body ("In summary, …") | Cut it |
| The same caveat in several places | State it once, where it applies |
| Every point that came to mind, unranked | Keep the points that bear on the reader's question: the important ones first and in full, the minor ones in a line or not at all |
| A change of topic with no stated link | Add the sentence that links them, reorder, or move the passage |
| "Additionally", "Furthermore", "Moreover" chaining unrelated points | Organize by the real relation (cause, sequence, contrast), or split them |
| Process details first, the conclusion last | The conclusion first, details as needed |

## 2. Stock vocabulary

Check: is there a plainer word that says the same thing, or a concrete fact the word is standing in for?

| Pattern | Rewrite |
|---|---|
| leverage, utilize | use |
| facilitate, enable (as filler) | help, let, or name what becomes possible |
| delve into, dive into | look at, examine, cover |
| crucial, pivotal, vital, key (as filler) | important, or say why it matters |
| robust | name the property: "retries three times", "handles empty input" |
| seamless, seamlessly | say what does not break or need a manual step |
| comprehensive | say what is covered |
| showcase, highlight, underscore | show |
| enhance, elevate | improve, and say how |
| landscape, ecosystem (abstract) | the actual set: "the CI providers we support" |
| myriad, plethora, numerous | many, or the number |

## 3. Inflated verbs for "is" and "has"

Check: does the verb do more than "is" or "has"?

| Pattern | Rewrite |
|---|---|
| The module serves as the entry point | The module is the entry point |
| The CLI boasts three output modes | The CLI has three output modes |
| This file stands as the single source | This file is the single source |

## 4. Framing devices

Check: does the frame add information, or only rhythm?

| Pattern | Rewrite |
|---|---|
| It's not just a cache, it's a consistency layer | It keeps reads consistent across workers |
| Not only X, but also Y | State X and Y as two facts, or keep only the one that matters |
| Three parallel items forced out of two ideas | List the items that exist |
| From startup time to memory use to error messages | Startup time, memory use, and error messages |
| The same idea named three ways (worker, runner, executor) | Pick one name and repeat it |

## 5. Trailing clauses and vague sources

Check: does the clause after the comma make a claim nobody stated or supported?

| Pattern | Rewrite |
|---|---|
| …, ensuring reliability across platforms | A separate sentence that names who ensures what, or cut it |
| …, highlighting the need for better tests | Cut it, or state the finding with its evidence |
| Experts agree that…, It is widely believed that… | Name the source, or cut the claim |

## 6. Metaphor posing as a technical noun

Check: is the word literal in this field? If it is a metaphor, use the literal word. Keep it where the field uses it literally, such as a process boundary.

| Pattern | Rewrite |
|---|---|
| the API surface | the exported functions, the endpoints |
| response shape | response fields |
| a ratchet on warnings | a warning count that may only go down |
| north star | goal |
| flywheel | name the loop: "more users report bugs, so fixes come faster" |
| wedge in a check | add a check |
| a new vector for errors | a new way for errors to happen |
| substrate | base, underlying layer |

## 7. Filler and hedging

Check: does the sentence lose anything without the phrase?

| Pattern | Rewrite |
|---|---|
| In order to | To |
| Due to the fact that | Because |
| It is important to note that | Cut it and state the point |
| It could potentially be the case that it might | It may |
| At the end of the day, Ultimately (as filler) | Cut it |

## 8. Chat phrases, flattery, and stock endings

Check: would a colleague say this at the end of a working conversation?

| Pattern | Rewrite |
|---|---|
| Great question!, You're absolutely right! | Cut it and answer |
| Certainly!, Of course! | Cut it |
| I hope this helps!, Let me know if you have any questions | Cut it, or ask the one question you actually need answered |
| This lays the groundwork for future success | The concrete next step, or nothing |

## 9. Hidden actors and weak verbs

Check: who does it, and what exactly happens?

| Pattern | Rewrite |
|---|---|
| Validation is performed on the input | The parser validates the input |
| The file was deleted | The cleanup job deleted the file (or "someone" when the actor is unknown) |
| perform an update of the index | update the index |
| significantly improves load time | cuts load time from 2.1 s to 0.4 s |
| runs very quickly | the number, or "is fast" when no number exists |

## 10. Over-compression

Check: can the reader read it aloud as a sentence?

| Pattern | Rewrite |
|---|---|
| cache miss → refetch, no retry | On a cache miss, the client fetches the data again and does not retry |
| Done; 3/3 green, 0 skip | All three tests passed and none were skipped |
| cfg val fails → exit 2 | When configuration validation fails, the command exits with code 2 |

## 11. Working labels and process residue

Check: has the reader seen this label, and does the sentence report a result or a history?

| Pattern | Rewrite |
|---|---|
| Went with option B | Built the index first, then migrated the data |
| Per Q3, the TTL stays at 60 s | The cache entries expire after 60 s |
| This used to retry; it no longer does | It does not retry |
| As discussed in review, … | State the decision |
| I first checked the logs and then found… | The logs show… |

## 12. Punctuation and formatting

- Em dashes: at most one per paragraph; a comma or a new sentence usually reads better.
- Colons: before a list or an example, not as a connector in the middle of a sentence.
- Bold: only for the words a reader must see first.
- A bold label that restates its line ("**Performance:** Performance improved") becomes prose.
- No emoji in headings or lists.
- Headings only where a reader needs to find a section; a short answer needs none.
- Heading case, quote style, and whether em dashes are allowed at all follow the project's house style.

## Exceptions

The field's established terms stay, even when they look like jargon to an outsider: a mutation in mutation testing, a facade in the Facade pattern, a primitive type. So do the project's own names, including product names that happen to be metaphors.
