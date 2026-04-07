# DocuBot Model Card

This model card is a short reflection on your DocuBot system. Fill it out after you have implemented retrieval and experimented with all three modes:

1. Naive LLM over full docs  
2. Retrieval only  
3. RAG (retrieval plus LLM)

Use clear, honest descriptions. It is fine if your system is imperfect.

---

## 1. System Overview

**What is DocuBot trying to do?**  
Describe the overall goal in 2 to 3 sentences.

It will answer questions that the user prompts it with about the documentation. It should give answers that are as concise and accurate as possible.

**What inputs does DocuBot take?**  
For example: user question, docs in folder, environment variables.

The docubot is looking at .md and .txt files from a docs folder. When the program runs, it will take user input (a number or letter 'q' to select either the model answering option or to quit, followed by the user's actual question).

**What outputs does DocuBot produce?**

Based on user choice it can answers questions one of 3 ways:
- A naive response by analyzing all documents at once
- Pure snippets of text retrieved from documents that matched best with the question
- RAG responses (combining top two approaches)

---

## 2. Retrieval Design

**How does your retrieval system work?**  
Describe your choices for indexing and scoring.

- How do you turn documents into an index?
- How do you score relevance for a query?
- How do you choose top snippets?

To index: It will parse through each word in each document, normalize it (remove plural s's, remove punctuation, and make all words lowercase), and use them as keys in a dictionary. These words will be mapped to the corresponding documents in which they can be found.
- Words from each next-line section of each document are given a tallied-up score based on appearance of each word from the question. Whichever top 3 sections have the highest scores (and no less than a score of 2) will be used in the final output. A previous next-line section will be included in the output for proper context.
- Top snippets are chosen using a minimum score value of 2 and the scoring system that I mentioned in the previous bullet point.

**What tradeoffs did you make?**  
For example: speed vs precision, simplicity vs accuracy.

It's a very simplified scoring system. In the future, I could have used something like "TF-IDF"

---

## 3. Use of the LLM (Gemini)

**When does DocuBot call the LLM and when does it not?**  
Briefly describe how each mode behaves.

- Naive LLM mode:
- Retrieval only mode:
- RAG mode:

- Naive: Prepends the question prompt to Gemini with the full corpus text and answers using that jumble of information
- Retrieval only: Provides snippets of information based on scores for matching words from the question and words from sections of text in the documents
- RAG: Only uses retrieval snippets of info as LLM input to provide a more accurate, better-organized response

**What instructions do you give the LLM to keep it grounded?**  
Summarize the rules from your prompt. For example: only use snippets, say "I do not know" when needed, cite files.

If the score for the retrieved snippets is lower than 2, nothing will be retrieved, defaulting to the "I do not know" response. So, loose answers will not be easily given. Top 3 answers also provides the bot with more chances of retrieving the right pool of information (as opposed to just one answer). All files are cited in the retrieval process.

---

## 4. Experiments and Comparisons

Run the **same set of queries** in all three modes. Fill in the table with short notes.

You can reuse or adapt the queries from `dataset.py`.

| Query | Naive LLM: helpful or harmful? | Retrieval only: helpful or harmful? | RAG: helpful or harmful? | Notes |
|------|---------------------------------|--------------------------------------|---------------------------|-------|
| How do I connect to the database? |harmful|helpful|helpful|Sometimes Naive will just infodump entire documents with information not relevant to the question.|
| Which endpoint lists all users? |helpful|helpful|helpful|This was a straightforward question with a direct answer.|

(I ran out of credits before getting to experiment extensively)

**What patterns did you notice?**  

- When does naive LLM look impressive but untrustworthy?
    - When you ask it open-ended questions, it will infodump entire documents at random sections without properly addressing the question.
- When is retrieval only clearly better?
    - Straightforward questions with simple answers (otherwise it is a bit hard to get the right context window for the entire answer).
- When is RAG clearly better than both?
    - When a detailed explanation is needed for an open-ended question.

---

## 5. Failure Cases and Guardrails

**Describe at least two concrete failure cases you observed.**  
For each one, say:

- What was the question?  
- What did the system do?  
- What should have happened instead?

1. Q: How do I connect to the database?
- Naive response info-dumped whole document texts instead of addressing problem concisely.

2. I cannot find the question, but sometimes, if you ask RAG or retrieval a very open-ended question about the documentation, since retrieval may not be able to find sufficient evidence (or the evidence itself might not have captured enough information with its small text window), RAG will also fail since it can only rely on the sometimes unreliable retrieval output.

**When should DocuBot say “I do not know based on the docs I have”?**  
Give at least two specific situations.

- You ask a question with only one word that could be relevant to the documentation.
- You ask a nonsensical question like "Hellooo? Who's there??"

**What guardrails did you implement?**  
Examples: refusal rules, thresholds, limits on snippets, safe defaults.

Minimum score limit of 2. Empty response will return an "I don't know."
Snippets are also only 2 new-line sections.

---

## 6. Limitations and Future Improvements

**Current limitations**  
List at least three limitations of your DocuBot system.

1. Scoring system too simplistic - word frequency not accounted for
2. Retrieval output sometimes misses context with its text window
3. Scoring system too simplistic - Equal scoring weight given to both something like "authentication" and "the"

**Future improvements**  
List two or three changes that would most improve reliability or usefulness.

1. TD-IDF scoring
2. Word frequency count in scoring

---

## 7. Responsible Use

**Where could this system cause real world harm if used carelessly?**  
Think about wrong answers, missing information, or over trusting the LLM.

If a dev is updating some kind of cybersecurity, medical, or financial app with the help of this program without briefly verifying answers could sometimes lead to large-scale issues (especially if said app is being used by the general public).

**What instructions would you give real developers who want to use DocuBot safely?**  
Write 2 to 4 short bullet points.

- Definitely make sure to briefly cross-verify these output results.
- Treat its responses more as a guideline for what to look for. 
- Try to keep your questions concise and relevant to the documentation for best results.

---
