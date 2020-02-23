
#------------------ Installations ------------------ 
if (!require(readxl)) install.packages('readxl')
if (!require(car)) install.packages('car')
if (!require(openxlsx)) install.packages('openxlsx')
if (!require(qcc)) install.packages('qcc')
if (!require(data.table)) install.packages('data.table')
if (!require(fastDummies)) install.packages('fastDummies')
if (!require(rstudioapi)) install.packages('rstudioapi')

#------------------ Imports ------------------ 
library("readxl")
library("car")
library("openxlsx")
library("qcc")
library("data.table")
library("fastDummies")
library("rstudioapi")
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
set.seed(100)

#------------------ Data Prep ------------------ 
df_auction = read_excel("./eBayAuctions.xls")
#View(df_auction)

# Train Test Split
train_indices = sample(seq_len(nrow(df_auction)), size = floor(0.60*nrow(df_auction)))

df_train = df_auction[train_indices,]
df_test = df_auction[-train_indices,]

# Save files (not compulsory)
write.xlsx(df_train, "train.xls", sheetName = "Sheet1", col.names = TRUE, row.names = FALSE, append = FALSE)
write.xlsx(df_test, "test.xls", sheetName = "Sheet1", col.names = TRUE, row.names = FALSE, append = FALSE)

#------------------ Pivot Tables --------------
# Category Pivot Table
df_pv_cat = setNames(aggregate(df_train[, 8], list(df_train$Category), mean),c("Category", "Competitive?"))

# Currency Pivot Table
df_pv_cur = setNames(aggregate(df_train[, 8], list(df_train$currency), mean),c("currency", "Competitive?"))

# Duration Pivot Table
df_pv_dur = setNames(aggregate(df_train[, 8], list(df_train$Duration), mean),c("duration", "Competitive?"))

# Category endDay Table
df_pv_end = setNames(aggregate(df_train[, 8], list(df_train$endDay), mean),c("endDay", "Competitive?"))

#------------------- Grouping ------------------
tc = df_train
# Category Grouping
df_train$Category = recode(df_train$Category, '"Health/Beauty" = "cat_1" ;
                                            "Coins/Stamps" = "cat_5" ;
                                            "EverythingElse" = "cat_2" ; 
                                            "Automotive" = "cat_4" ;
                                            "Jewelry" = "cat_4" ;
                                            "Books" = "cat_6" ; 
                                            "Toys/Hobbies" = "cat_6" ;
                                            "Business/Industrial" = "cat_8" ;
                                            "Antique/Art/Craft" = "cat_6" ;
                                            "Clothing/Accessories" = "cat_6" ;
                                            "Pottery/Glass" = "cat_3" ;
                                            "Collectibles" = "cat_7" ;
                                            "Music/Movie/Game" = "cat_7" ;
                                            "Home/Garden" = "cat_9" ;
                                            "Electronics" = "cat_10" ;
                                            "Computer" = "cat_9" ;
                                            "SportingGoods" = "cat_9" ;
                                            "Photography" = "cat_11" ')

# Currency Grouping
df_train$currency = recode(df_train$currency,'"EUR" = "cur_1" ; "GBP" = "cur_2" ; "US" = "cur_1"')

# Duration Grouping
df_train$Duration = recode(df_train$Duration, '"3" = "dur_1" ; "7" = "dur_1" ; "1" = "dur_2" ; "10" = "dur_2" ; "5" = "dur_3"')

# endDay Grouping
df_train$endDay = recode(df_train$endDay, '"Fri" = "day_2" ; "Wed" = "day_1" ; "Tue" = "day_2" ; "Thu" = "day_3" ;
                                          "Sun" = "day_1" ; "Sat" = "day_1" ;  
                                          "Mon" = "day_3"')

#------------------ Build Fit All Model ------------------
# Data prep
df_train_dum = dummy_cols(df_train, select_columns = c("Category","currency", "endDay", "Duration"))
df_train_dum = df_train_dum[,!(names(df_train_dum) %in% c("Category","currency", "endDay", "Duration"))]

# Build Model
fit_all <- glm(`Competitive?` ~.,family = binomial(link = 'logit'), data = df_train_dum)
coefs = setNames(setDT(as.data.frame(summary(fit_all)$coefficients), keep.rownames = TRUE)[], c("Predictor", "Estimate", "StdError", "zValue", "p>|z|"))
View(coefs)

#------------------ Build Single Model ------------------ 
# Get Highest Coefficient
ordered_coefs = coefs[order(-coefs$Estimate),]
high_pred = toString(ordered_coefs[1,1])
print(paste0("Highest Coefficient Predictor: ",high_pred))

# Build Model
subset = c("Competitive?", high_pred)
fit_single = glm(`Competitive?` ~., family = binomial(link = 'logit'), data = df_train_dum[subset])
coefs_single = setNames(setDT(as.data.frame(summary(fit_single)$coefficients), keep.rownames = TRUE)[], c("Predictor", "Estimate", "StdError", "zValue", "p>|z|"))
View(coefs_single)

#------------------ Build Reduced Model ------------------ 
# Get All Significant Predictors
significance_level = 0.05
sig_pred = summary(fit_all)$coefficients
significant_predictors = sig_pred[sig_pred[,4] < significance_level,]
significant_predictors = setNames(setDT(as.data.frame(significant_predictors), keep.rownames = TRUE)[], c("Predictor", "Estimate", "StdError", "zValue", "p>|z|"))
print(paste0("All Significant Predictors: ",as.vector(significant_predictors$Predictor)))

# Build Model
subset_sig = c("Competitive?",as.vector(significant_predictors$Predictor))
fit_reduced = glm(`Competitive?` ~., family = binomial(link = 'logit'), data = df_train_dum[subset_sig])
coefs_red = setNames(setDT(as.data.frame(summary(fit_reduced)$coefficients), keep.rownames = TRUE)[], c("Predictor", "Estimate", "StdError", "zValue", "p>|z|"))
View(coefs_red)

#-----------Comparing Models------------
anova(fit_reduced, fit_all, test = 'Chisq')

#-----------Checking for Over Dispersion------------

s = rep(length(df_train_dum$`Competitive?`), length(df_train_dum$`Competitive?`))
qcc.overdispersion.test(df_train_dum$`Competitive?`, size = s, type = "binomial")











