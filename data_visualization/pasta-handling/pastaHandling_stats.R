
library(rstatix)
library(tidyverse)

pastaData <- read.csv(file = "/Users/Krista/OneDrive - Umich/figures/pastaHandling_20210708.csv")

### Question: Is there a group difference between control and KO for various behaviors 
###           (e.g., left_forepaw_failure_to_contact, drops, etc)?

## Poisson Regression

# forepaw adjustments - use MASS::glm.nb (NS)
pastaData$forepaw_adjustments <- pastaData$left_forepaw_adjustments + pastaData$right_forepaw_adjustments
forepawAdjperMouse <- pastaData %>% group_by(genotype, eartag) %>% summarize(avgforepaw_adj=mean(forepaw_adjustments), forepaw_adjustments=sum(forepaw_adjustments), trials=n())
forepawAdj_model <- glm(forepaw_adjustments ~ genotype + offset(log(trials)), forepawAdjperMouse, family=quasipoisson())
forepawAdj_model2 <- MASS::glm.nb(forepaw_adjustments ~ genotype + offset(log(trials)), forepawAdjperMouse)

# forepaw failure to contact - use glm (NS)
pastaData$forepaw_failure_to_contact <- pastaData$left_forepaw_failure_to_contact + pastaData$right_forepaw_failure_to_contact
forepawContactperMouse <- pastaData %>% group_by(genotype, eartag) %>% summarize(avgforepaw_contact=mean(forepaw_failure_to_contact), forepaw_failure_to_contact=sum(forepaw_failure_to_contact), trials=n())
forepawContact_model <- glm(forepaw_failure_to_contact ~ genotype + offset(log(trials)), forepawContactperMouse, family=poisson())
forepawContact_model2 <- MASS::glm.nb(forepaw_failure_to_contact ~ genotype + offset(log(trials)), forepawContactperMouse)

# guide grasp switch - use glm (NS)
ggswitchperMouse <- pastaData %>% group_by(genotype, eartag) %>% summarize(avgGGswitch=mean(guide_grasp_switch), guide_grasp_switch=sum(guide_grasp_switch), trials=n())
ggswitch_model <- glm(guide_grasp_switch ~ genotype + offset(log(trials)), ggswitchperMouse, family=poisson())
ggswitch_model2 <- MASS::glm.nb(guide_grasp_switch ~ genotype + offset(log(trials)), ggswitchperMouse)

# drops - use glm (*)
dropsperMouse <- pastaData %>% group_by(genotype, eartag) %>% summarize(avgdrops=mean(drops), drops=sum(drops), trials=n())
drops_model <- glm(drops ~ genotype + offset(log(trials)), dropsperMouse, family=poisson())
drops_model2 <- MASS::glm.nb(drops ~ genotype + offset(log(trials)), dropsperMouse)

# mouth_pulling - use glm (NS)
pullsperMouse <- pastaData %>% group_by(genotype, eartag) %>% summarize(avgpulls=mean(mouth_pulling), mouth_pulling=sum(mouth_pulling), trials=n())
pulls_model <- glm(mouth_pulling ~ genotype + offset(log(trials)), pullsperMouse, family=poisson())
pulls_model2 <- MASS::glm.nb(mouth_pulling ~ genotype + offset(log(trials)), pullsperMouse)

# mouth_pulling - use glm (NS)
pullsperMouse <- pastaData %>% group_by(genotype, eartag) %>% summarize(avgpulls=mean(mouth_pulling), mouth_pulling=sum(mouth_pulling), trials=n())
pulls_model <- glm(mouth_pulling ~ genotype + offset(log(trials)), pullsperMouse, family=poisson())
pulls_model2 <- MASS::glm.nb(mouth_pulling ~ genotype + offset(log(trials)), pullsperMouse)

# pasta_long_paws_together - use glm (NS)
pasta_longperMouse <- pastaData %>% group_by(genotype, eartag) %>% summarize(avgpasta_long=mean(pasta_long_paws_together), pasta_long_paws_together=sum(pasta_long_paws_together), trials=n())
pasta_long_model <- glm(pasta_long_paws_together ~ genotype + offset(log(trials)), pasta_longperMouse, family=poisson())
pasta_long_model2 <- MASS::glm.nb(pasta_long_paws_together ~ genotype + offset(log(trials)), pasta_longperMouse)

# pasta_short_paws_apart - use glm (NS)
pasta_shortperMouse <- pastaData %>% group_by(genotype, eartag) %>% summarize(avgpasta_short=mean(pasta_short_paws_apart), pasta_short_paws_apart=sum(pasta_short_paws_apart), trials=n())
pasta_short_model <- glm(pasta_short_paws_apart ~ genotype + offset(log(trials)), pasta_shortperMouse, family=poisson())
pasta_short_model2 <- MASS::glm.nb(pasta_short_paws_apart ~ genotype + offset(log(trials)), pasta_shortperMouse)

# Time to Eat - (NS)
eatTime_perMouse <- pastaData %>% group_by(genotype, eartag) %>% summarize(avgEatTime=mean(time_to_eat), time_to_eat=sum(time_to_eat), trials=n())
eatTime_model <- glm(time_to_eat ~ genotype + offset(log(trials)), eatTime_perMouse, family=gaussian())
