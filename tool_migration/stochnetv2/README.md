# StochNetV2 migration

The `stochnet_v2` directory contains the StochNetV2 deep abstraction tool with heavily modified source code to achieve the below objectives.

## Objectives
- [x] Adjust source code to be compatible with TensorFlow 2 (either complete migration or via the compatibility layer)
- [x] Adjust source code to be runnable on `arm64` (M-series chips) machines
- [x] Implement a compatibility layer between Tellurium's stochastic simulations and StochNetV2's training data input
- [ ] Successfully produce simulation traces by a StochNetV2 model trained on Tellurium simulation data