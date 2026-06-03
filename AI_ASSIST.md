# AI Assist Report

> Task 8: Fill in all three sections below. Your reflection should be specific —
> describe exactly what you asked, what the AI returned, and what you changed.
> "The AI fixed it" is not enough detail.

## The prompt I gave

My pull request checks were failing even though my own CI workflow had passed. GitHub only showed that the HYF autograder ran `bash test.sh` and exited with code 1. I asked ChatGPT to help me understand what was failing and how to debug the autograder output.

I also shared the output from running the grader locally, including:

```bash

bash .hyf/test.sh > test-output.txt 2>&1
echo $?
cat test-output.txt
```
and then the trace output from:

```
bash -x .hyf/test.sh
```

## The code or suggestion it returned

The assistant suggested that the visible GitHub error was not enough, because it only showed that test.sh exited with code 1. It suggested running the autograder locally with shell trace mode:

```
bash -x .hyf/test.sh
```

The assistant then helped me read the trace. The important part of the trace showed that the grader was checking all Python files inside src/, not only the main pipeline file. It found several old print() calls:

```
src/ingest_files.py: print(...)
src/ingest_api.py: print(...)
src/validate.py: print(...)
```

The assistant also pointed out that the grader was searching for the text NotImplementedError in src/pipeline.py. In my case, this text was not executable code anymore. It was leftover starter-template text inside the docstring, but the static grader still detected it.

The assistant suggested checking the project with:

```
grep -R "NotImplementedError\|print(" src tests
```

and then removing the leftover print() calls and the leftover NotImplementedError text.

## What I changed after reviewing it

After reviewing the trace, I removed the old debug print() calls from the helper modules:

```
src/ingest_api.py
src/ingest_files.py
src/validate.py
```

These print() calls were left over from the Week 3 version of the pipeline and were only used for manual debugging. The Week 5 assignment requires logging instead of print() for pipeline status, and the autograder checks all files under src/.

I also removed the leftover NotImplementedError text from the docstring in src/pipeline.py. It was not part of running code, but the static grader still searched for that string and marked it as a remaining starter stub.

After making those changes, I reran:

```
ruff check src tests
ruff format --check src tests
pytest -q
bash .hyf/test.sh
```

The checks passed after the cleanup. This was useful because the problem was not in the pipeline logic or Dockerfile. The issue was leftover debug output and starter-template text that the autograder detected during static analysis.