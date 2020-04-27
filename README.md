# Rapid MVP/PoC API + admin development with Django and Django-Rest-Framework

**TL/DR:** `Simplicity` ∩ `Interactive-REPL-driven-development` == ❤️.

---

> ⚠️ work in progress - for now intended only for author's own use ⚠️

---

## Problem this solves

While using an "ancient" monolythic framework like Django is far from best-practice in 2020, sometimes you need to quickly whip up an MVP or Proof-of-Concept. If most of the technical aspects of your app are pretty unremarkable (eg. the interesting part is the business problem, business logic, maybe some machine learning model secret sauce etc.), it might be a good idea to rely on boring established technology and benefit from:

- decent documentation *(though often outdated and/or wrong)*
- easy cookbook/recipe style solutions to most problems you may have *(...that rarely fit you problem well, but often they're "good enough")*
- lots of libs, plugins etc. that already solve most of your needs *(many unmaintained or of dubious quality...)*
- access to easily affordable expertise *(but... "what you pay is what you get!")*

**DISCLAIMER:** Picking Django + friends will bring in a lot of invisible "potential technical debt" and "complexity cost - if you're in a *startup-type environment* and **sustainable**-*agility* is what matters most (more than, ahem, "cheap devs"...), picking a more adapted-to-the-task, sane, and modern stack like eg. [FastAPI](https://github.com/tiangolo/fastapi) is a better idea than this. YMMV.

# TODO
 In no specific order:
 - [ ] write README
 - [ ] add `Dockerfile` and `docker-compose` (extract from a working project based on this pattern or copy from [cookiecutter-django](https://github.com/pydanny/cookiecutter-django))
 - [ ] write extended docs
 - [ ] add snippets and examples
 - [ ] (maybe) refactor as a proper [cookiecutter](https://github.com/cookiecutter/cookiecutter)
 - [ ] add testing examples & tools
 - [ ] include linters and formatters (flake8, black)
 - [ ] include mypy typechecker config
 - [ ] include `.editorconfig`
 - [ ] include `django-allauth` + configs examples
 - [ ] include standalone frontend example(s) (with auth code)
