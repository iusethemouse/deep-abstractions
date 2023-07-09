# Deep Abstractions
###### Terminology
- __Stochastic Chemical Reaction Network__ (SCRN): a mathematical model used to describe the dynamics of chemical reactions in a stochastic manner, taking into account the randomness inherent in the reaction processes.
- __Deep Abstractions__ (DA): computational models or techniques that employ deep neural networks to abstract and approximate the behavior of SCRNs by learning their probabilistic dynamics.
- __Neural Architecture Search__ (NAS): a technique or methodology that automates the process of designing or discovering optimal neural network architectures by exploring a search space of possible architectures and using optimization strategies to find architectures that perform well on a given task or dataset.

---

This work is part of my Master thesis, aiming to:
1. Evaluate existing neural network-based approaches to SCRN abstractions.
2. Evaluate the applicability and value of NAS to the problem of finding an optimal neural network for a given SCRN.
3. Produce an open-source GUI tool that utilises the results of the above evaluations to provide a no-code way for researchers to make use of neural network-based SCRN abstraction methods.

This repository contains the code produced as the result of the above.

## What this aims to solve
### Method fragmentation
While no longer in its infancy, the area of deep abstractions for SCRNs is still rather young. Over the past five years, researchers and developers focussed on utilising all sorts of neural network architectures and pipeline designs in their DA tools.

Each DA method would rely on one of the tools available in the relatively mature ecosystem of Python packages providing stochastic simulation capabilities (e.g. GillesPy2, StochPy, cayenne, Tellurium, among others). This naturally leads to fragmentation in what the neural network expects as training data, or input, and what kind of data it produces once trained. This means that performing comparisons between the different methods using specific SCRN definitions is far from trivial.

>Using a __common SCRN definition format__ together with a __single stochastic simulation framework__ for all DA methods would allow to perform fair and consistent comparative evaluation of their accuracy and performance.

- __Selected SCRN definition formats__: [SBML](https://sbml.org) (.xml) & [Antimony](https://tellurium.readthedocs.io/en/latest/antimony.html) (human-readable)
- __Selected stochastic simulation framework__: [Tellurium](https://tellurium.readthedocs.io/en/latest/)

### Poor user experience
Shared between all DA methods developed up to now is a lack of complexity abstraction. Namely, a user of these methods would need to posess the following:
- a firm grasp of programming in Python
- familiarity with command-line interfaces
- ability to navigate complex codebases with little to no documentation
- a certain level of expertise with neural networks

>The "complexity abstraction" mentioned above can come in many ways, one of which is "wrapping" the implementation of the DA method in a graphical user interface. Combined with NAS, this would alleviate a large number of obstacles preventing researchers from using these tools.

- Selected GUI framework: [KNIME Analytics Platform](https://www.knime.com/knime-analytics-platform) via a [Python-based extension](https://docs.knime.com/latest/pure_python_node_extensions_guide/index.html#introduction)

---

## Outcomes
As a concrete outcome of this work, an open-source KNIME extension will be available for researchers to use and contribute to. The planned v1.0.0 functionality:
- Reading and writing SCRN models in SBML and Antimony formats.
- Performing stochastic simulations of SCRN models using "classic" methods such as SSA, Tau-leaping, and others.
- Using the generated trajectories as training data for a state-of-the-art neural network-based deep abstraction model.
- Reading and writing trained deep abstraction models in common formats.
- Performing stochastic simulations of SCRN models using deep abstractions models.

Additionally, all the DA methods evaluated will be available in their modified state (e.g. common input data, etc.), allowing others to replicate the experiments or perform their own.

# Milestones
- [x] Add initial nodes for reading, writing, and visualising SCRN models (SBML and Antimony formats)
- [x] Add initial nodes for performing and visualising stochastic simulations using Tellurium
- [x] Develop a "baseline" deep abstraction method to compare other methods to
- [x] Modify StochNetV2 to accept training datasets generated by Tellurium instead of Gillespy
- [ ] Add initial nodes for training StochNetV2 models and generating stochastic simulations using these models
- [ ] Modify the GAN deep abstraction tool to accept training datasets generated by Tellurium instead of StochPy
- [ ] Add initial nodes for training GAN models and generating stochastic simulations using these models
- [ ] Write a parser to convert SCRN definitions from Antimony to NNCME's custom PyTorch-based definition format
- [ ] Add initial nodes for training NNCME models and generating stochastic simulations using these models
- [ ] Add nodes for peforming model evaluations
- [ ] Outline the best-performing method using the evaluation tools
- [ ] Integrate NAS into the method and verify whether its use is applicable
- [ ] Modify the method to maximise accuracy and performance using state-of-the-art deep learning techniques
- [ ] Add initial nodes for using the method for training on and generating stochastic simulations