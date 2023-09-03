import knime.extension as knext

main_category = knext.category(
    path="/",
    level_id="deep_abstractions",
    name="Deep Abstractions of CRNs",
    description="Nodes for Deep Learning Abstractions of Chemical Reaction Networks",
    icon="src/assets/icons/icon.png",
)

reaction_networks_category = knext.category(
    path=main_category,
    level_id="reaction_networks",
    name="CRN",
    description="Nodes for handling CRN definitions",
    icon="src/assets/icons/icon.png",
)

simulations_category = knext.category(
    path=main_category,
    level_id="simulations",
    name="SSA",
    description="Nodes for performing stochastic simulations of CRNs using SSA",
    icon="src/assets/icons/icon.png",
)

deep_abstractions_category = knext.category(
    path=main_category,
    level_id="deep_abstractions",
    name="Deep Abstraction",
    description="Nodes for handling deep abstractions of CRNs",
    icon="src/assets/icons/icon.png",
)
