# ai-doc-gen docs

AI-powered documentation generator. Uses models such as Ollama and Llama to
inspect a codebase and produce structured project documentation automatically.

## Overview

Run the generator via `invoke` and the generated docs are written into the
`docs/` folder. Useful for keeping README-style documentation in sync with the
code without manual writing.

## Features

- Automatic documentation generation from source inspection
- Ollama / Llama powered inference
- Outputs structured markdown into `docs/`

## Quickstart

```bash
git clone https://github.com/charudatta10/ai-doc-gen.git
cd ai-doc-gen
pip install -r requirements.txt
invoke
```

## See also

- Main project [README](../README.md)
- [FAQ](faq.md)
- [Features](features.md)
- [Getting started](getting-started.md)
- [Algorithm](algorithm.md)
- [Reference](reference.md)
- [Contributing](contributing.md)