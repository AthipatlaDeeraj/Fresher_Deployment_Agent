from fda.services.rule_engine.r1_low_junior import R1LowJuniorRatio
from fda.services.rule_engine.r2_high_fresher import R2HighFresherIntake
from fda.services.rule_engine.r3_deployment import R3FresherDeployment
from fda.services.rule_engine.r4_training import R4TrainingSuggestions

# Expose a list of all active rules
ACTIVE_RULES = [
    R1LowJuniorRatio(),
    R2HighFresherIntake(),
    R3FresherDeployment(),
    R4TrainingSuggestions()
]
