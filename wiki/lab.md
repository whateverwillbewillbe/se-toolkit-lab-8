# Lab

<h2>Table of contents</h2>

- [What is a lab](#what-is-a-lab)
- [Set up the lab repository directory](#set-up-the-lab-repository-directory)
  - [Clone the lab repository](#clone-the-lab-repository)
  - [Enter the lab repository directory](#enter-the-lab-repository-directory)
- [Constants](#constants)
  - [`<lab-repo-name>`](#lab-repo-name)
- [Prompts for coding agents](#prompts-for-coding-agents)
  - [Make the task instructions linear](#make-the-task-instructions-linear)
  - [Give directions on solving the task](#give-directions-on-solving-the-task)

## What is a lab

A lab is the time for learning:

- under the supervision of a TA
- together with your classmates
- with the help of AI assistants (chatbots, [coding agents](./coding-agents.md#what-is-a-coding-agent), etc.)

## Set up the lab repository directory

Complete these steps:

<!-- no toc -->
1. [Clone the lab repository](#clone-the-lab-repository).
2. [Enter the lab repository directory](#enter-the-lab-repository-directory).
3. [Fetch the branch `<branch>`](./git-vscode.md#fetch-the-branch-branch-using-the-vs-code-terminal).
4. [Switch to the branch `<branch>`](./git-vscode.md#switch-to-the-branch-branch-using-the-vs-code-terminal).

### Clone the lab repository

1. [Clone the lab repository](./git-vscode.md#clone-the-repository-using-the-vs-code-terminal).

   Replace the placeholders:

   - `<repo-url>` with `https://github.com/<your-github-username>/se-toolkit-lab-7`

   - `<path>` with `~/se-toolkit-lab-7`

   - [`<your-github-username>`](./github.md#your-github-username-placeholder)

### Enter the lab repository directory

1. To enter the lab repository directory,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   cd ~/se-toolkit-lab-7
   ```

2. [Clone the lab repository](#clone-the-lab-repository) if the directory doesn't exist.

## Constants

### `<lab-repo-name>`

`se-toolkit-lab-7` (without `<` and `>`).

## Prompts for coding agents

> [!IMPORTANT]
> It's recommended to use a [coding agent](./coding-agents.md#what-is-a-coding-agent)
> because it can read files in your repo and understand the project context
> better than an LLM in a web chat.

<!-- no toc -->
- [Make the task instructions linear](#make-the-task-instructions-linear)
- [Give directions on solving the task](#give-directions-on-solving-the-task)

### Make the task instructions linear

```md
Write complete instructions for @task-1 in tmp/instructions/task-1.md.

Substitute placeholders with concrete values.

Inline relevant instructions from wiki where necessary.
```

### Give directions on solving the task

```md
I want to maximize learning.

Give me directions on how to solve this task.

Why is this task important? 

What exactly do I need to do?
```
