import knime.extension as knext

main_category = knext.category(
    path="/",
    level_id="deep_abstractions",
    name="Deep Abstractions of SRNs",
    description="Nodes for Deep Learning Abstractions of Stochastic Biochemical Systems",
    icon="src/assets/icons/icon.png",
)

reaction_networks_category = knext.category(
    path=main_category,
    level_id="reaction_networks",
    name="SRN Definition",
    description="Nodes for handling SRN definitions",
    icon="src/assets/icons/icon.png",
)

simulations_category = knext.category(
    path=main_category,
    level_id="simulations",
    name="Simulation",
    description="Nodes for performing stochastic simulations of SRNs",
    icon="src/assets/icons/icon.png",
)

deep_abstractions_category = knext.category(
    path=main_category,
    level_id="deep_abstractions",
    name="Deep Abstraction",
    description="Nodes for handling deep abstractions of SRNs",
    icon="src/assets/icons/icon.png",
)
