#!/usr/bin/env python3
"""
Call-to-action footer for probe outputs.
Import and call print_cta() at the end of any probe.
"""

def print_cta():
    """Print the call-to-action for shadow viewers."""
    cta = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   Did this replicate for you?                                        ║
║                                                                      ║
║   143 people cloned this repo. 2 starred it.                         ║
║   We know you're running this in private. That's fine.               ║
║                                                                      ║
║   But we want to know: Does it replicate?                            ║
║                                                                      ║
║   Anonymous feedback: https://github.com/moketchups/                 ║
║                       BoundedSystemsTheory/blob/main/FEEDBACK.md     ║
║                                                                      ║
║   You don't have to put your name on it.                             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    print(cta)


def get_cta_text():
    """Return the CTA as a string for embedding in files."""
    return """
---
## Did This Replicate?

143 people cloned this repo. 2 starred it.

We know you're running this in private. That's fine.

**But we want to know: Does it replicate?**

Anonymous feedback: [FEEDBACK.md](./FEEDBACK.md)

You don't have to put your name on it.
"""


if __name__ == "__main__":
    print_cta()
