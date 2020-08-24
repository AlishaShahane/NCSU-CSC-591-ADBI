# Set working directory
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

# Install pcalg based on version
# vers <- getRversion()
# if (vers >= "3.6"){
#   if (!requireNamespace("BiocManager", quietly = TRUE))
#     install.packages("BiocManager")
    #   BiocManager::install(version = "3.10")
#   BiocManager::install(c("graph", "RBGL","Rgraphviz"))
# } else {
  # To install pcalg library you may first need to execute the following commands:
#   source("https://bioconductor.org/biocLite.R")
#   biocLite("graph")
#   biocLite("RBGL")
# }

# Load the libraries 
if (!require(vars)) install.packages('vars')
if (!require(urca)) install.packages('urca')
if (!require(ggm)) install.packages('ggm')
if (!require(devtools)) install.packages('devtools')
if (!require(rcausal)) install_github("bd2kccd/r-causal")
if (!require(DOT)) install.packages('DOT')
if (!require(stringr)) install.packages("stringr")
if (!require(rJava)) install.packages("rJava")

library(vars)
library(urca)
library(graph)
library(pcalg)
library(ggm)
library(devtools)
library(rcausal)
library(DOT)

require(Rgraphviz)
require(igraph)

# Read the input data 
df_input = read.csv('./data.csv')

# Build a VAR model 
# Select the lag order using the Schwarz Information Criterion with a maximum lag of 10
# see ?VARSelect to find the optimal number of lags and use it as input to VAR()
lags = VARselect(df_input, lag.max = 10, type = "const")$selection[3]
var_model = VAR(df_input, p = lags)

# Extract the residuals from the VAR model 
# see ?residuals
res_model = residuals(var_model)

# Check for stationarity using the Augmented Dickey-Fuller test 
# see ?ur.df
summary(ur.df(res_model[,'Move'],  type='trend'))
summary(ur.df(res_model[,'RPRICE'], type='trend'))
summary(ur.df(res_model[,'MPRICE'], type='trend'))

print("Test statistic for all variables are less than critical value.")
print("We reject the null hypothesis and all variables are stationary.")


# Check whether the variables follow a Gaussian distribution  
# see ?ks.test
ks.test(res_model[,'Move'], 'pnorm')
ks.test(res_model[,'RPRICE'], 'pnorm')
ks.test(res_model[,'MPRICE'], 'pnorm')

print("We reject the null hypothesis as p value is very low.")
print("This indicates that variables do not follow a Gaussian distribution.")

# Write the residuals to a csv file to build causal graphs using Tetrad software
write.csv(res_model, file = 'residuals.csv', row.names = FALSE)

df_res = read.csv("./residuals.csv")
tetradrunner.getAlgorithmDescription(algoId = 'fges')
#Compute FGES search
tetradrunner <- tetradrunner(algoId = 'fges',df = df_res,scoreId = 'sem-bic',
                             dataType = 'continuous',faithfulnessAssumed=TRUE,maxDegree=-1,verbose=TRUE)

tetradrunner$nodes #Show the result's nodes
tetradrunner$edges #Show the result's edges

graph <- tetradrunner$graph
graph$getAttribute('BIC')

nodes <- graph$getNodes()
for(i in 0:as.integer(nodes$size()-1)){
  node <- nodes$get(i)
  cat(node$getName(),": ",node$getAttribute('BIC'),"\n")
}


graph_dot <- tetradrunner.tetradGraphToDot(tetradrunner$graph)
dot(graph_dot)

# OR Run the PC and LiNGAM algorithm in R as follows,
# see ?pc and ?LINGAM 

# PC Algorithm
rows = nrow(res_model)
cols = colnames(res_model)
pc_algo = pc(suffStat = list(C = cor(res_model), n = rows), indepTest = gaussCItest, alpha = 0.1, labels = cols)

plot(pc_algo, main ="PC Algorithm")

# LiNGAM Algorithm
lingam_algo = lingam(res_model, verbose = TRUE)

d = dim(lingam_algo$Bpruned)

# Transpose because the lingam returns the adjacency matrix 
# such that [i,j] is edge from j to i
edL = t(lingam_algo$Bpruned)
colnames(edL) <- cols
rownames(edL) <- cols

g = graph.adjacency(edL, add.rownames = TRUE)
plot(g)

