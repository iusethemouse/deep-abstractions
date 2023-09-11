# Deep Abstractions
###### Terminology
- __Chemical Reaction Network__ (CRN): a mathematical formalism used to model the dynamics of complex systems by describing them in the form of species (e.g. molecules) and inter-species reactions that cause the system to evolve through time. CRNs can be used to model systems of various complexity, from a simple network with 3 species and 2 reactions modelling an epidemiological scenario, to highly complex systems comprising of tens of species and reactions.
- __Deep Abstractions__ (DA): a family of model reduction techniques that employ deep neural networks to learn the complex dynamics of CRNs from trajectories generated with conventional simulation methods, e.g. Gillespie's SSA. Trained abstract models can then emulate SSA by producing statistically similar simulation trajectories much faster.

---

This work is part of my Master thesis, a partical goal of which is to produce an open-source GUI tool that aims to mitigate usability and approachability problems related to using deep abstraction methods.

This repository contains the implementation of a KNIME extension, "Deep Abstractions of CRNs", which uses [Tellurium](https://github.com/sys-bio/tellurium) and [PyTorch](https://github.com/pytorch/pytorch) as the backend, and [KNIME Analytics Platform](https://github.com/knime/knime-core) as the frontend.

## What this aims to solve
### Method fragmentation
In the survey of DA methods undertaken for the Master thesis, it was established that each DA method generally relies on one of the multitude of tools available in the relatively mature ecosystem of Python packages providing stochastic simulation capabilities (e.g. GillesPy2, StochPy, cayenne, Tellurium, among others). This naturally leads to fragmentation in what the neural network expects as training data, or input, and what kind of data it produces upon inference. This means that performing comparisons between the different methods using specific CRN definitions is far from trivial.

>Using a __common CRN definition format__ together with a __single stochastic simulation framework__ for all DA methods would allow to perform fair and consistent comparative evaluation of their accuracy and performance.

- __Selected CRN definition formats__: [SBML](https://sbml.org) (.xml) & [Antimony](https://tellurium.readthedocs.io/en/latest/antimony.html) (human-readable)
- __Selected stochastic simulation framework__: [Tellurium](https://tellurium.readthedocs.io/en/latest/)

### Poor user experience
Shared between all DA methods developed up to now is a lack of complexity abstraction. In the present context, these are rather loaded terms, but what is precisely meant here is that a user of these methods would need to posess the following:
- a firm grasp of programming in Python
- familiarity with command-line interfaces
- ability to navigate complex codebases with little to no documentation
- a certain level of expertise with neural networks

>The "complexity abstraction" mentioned above can come in many ways, one of which is "wrapping" the implementation of the DA method in a graphical user interface.

- Selected GUI framework: [KNIME Analytics Platform](https://www.knime.com/knime-analytics-platform) via a [Python-based extension](https://docs.knime.com/latest/pure_python_node_extensions_guide/index.html#introduction)

---

## Available functionality
As a proof-of-concept, the current v0.1.0 implementation of the "Deep Abstractions of CRNs" extension provides the following functionality:
- Importing and exporting CRN models in SBML and Antimony formats. This additionally allows to perform direct translations from SBML to Antimony and vice versa.
- Performing stochastic simulations of CRN models using SSA. This produces trajectories as KNIME tables, as well as provides clear visualisations of the trajectories allowing for quickly exploring the various characteristics of the CRN's dynamics.
- Generating configurable training datasets using SSA.
- Training a Mixed Density Network (MDN) deep abstract model using the generated training trajectories.
- Importing and exporting trained deep abstract models as either PyTorch weights or using the universal [ONNX](https://github.com/onnx/onnx) format.
- Performing stochastic simulations of CRN models using deep abstract models.

---

## Documentation
