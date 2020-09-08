library(lme4)
library(tidyverse)
setwd("./Documents/grad_school_classes/nba-movement-data")

#read data for public model
first_df <- read.csv("./data/multi_level_model_first.csv")
#standardize first model prediction
first_df$first_model_value <- (first_df$first_model_value - mean(first_df$first_model_value)) / sd(first_df$first_model_value)
#seperate into train/test
first_train_df <- first_df[c(0:75000),]
first_test_df <- first_df[c(75000:nrow(df)),]
#train multilevel model
first_model <- glmer(SHOT_MADE_FLAG ~  first_model_value + (1 |shot_zone:shot_cluster), data=first_train_df,family=binomial(link="logit"),control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e5)))

#read data for private model
second_df <- read.csv("./data/multi_level_model_second.csv")
second_df$sec_model_value <- (second_df$sec_model_value - mean(second_df$sec_model_value)) / sd(second_df$sec_model_value)
second_train_df <- second_df[c(0:75000),]
second_test_df <- second_df[c(75000:nrow(df)),]
second_model <- glmer(SHOT_MADE_FLAG ~  sec_model_value + (1 | shot_zone:shot_cluster), data=second_train_df,family=binomial(link="logit"),control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e5)))


#get predictions
first_predictions <- predict(first_model,newdata=first_test_df,type="response")
#round to 0,1
guesses <- round(first_predictions)
truth <- first_test_df$SHOT_MADE_FLAG
#compare with ground truth
accuracy <- sum(guesses == truth) / length(truth)
print("FIRST MODEl ACCURACY")
print(accuracy)

second_predictions <- predict(second_model,newdata=test_df,type="response")
guesses <- round(second_predictions)
truth <- second_test_df$SHOT_MADE_FLAG
accuracy <- sum(guesses == truth) / length(truth)
print("SECOND MODEl ACCURACY")
print(accuracy)