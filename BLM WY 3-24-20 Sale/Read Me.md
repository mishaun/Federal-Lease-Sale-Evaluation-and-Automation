# Project Summary and Goals

This project has 2 main goals.

1.  Automate federal lease sale and auction process to dramatically increase internal efficiency.
The company evaluates, invests, and participates in multiple federal lease sales/auctions each quarter.
    
* Automation processes includes:
    1. Autofilling federal lease sale meta data through a developed webscraping tool
    2. Generating natural language summaries tract by tract for CEO to read in simple, paragraph text 
    3. Creating visual chart summaries, which display activity around the tract such as production, permits, and leasing details
    
2.  Build a model to predict prices, or bonuses, for tract for sale in area of interest by using historical lease pricing, permit, and production activity as input features

* Models used were multilinear regression and decision tree
    * **Due to high variablility in lease bonus prices from the market environment, machine learning models struggled to output respectable errors and results.  Therefore, the model predictions were weighed against many factors by the CEO.
    
    
# Code and Packages
1.  Code used: Python 3.7
2.  Packages used include:
    * Pandas, Geopandas, Seaborn, Matplotlib, Sklearn,
    * Selenium, Beautiful Soup, OS, pdfrw, Openpyxl
    
    
# Script and Notebook Overviews

## 1. Cleaning and Data Preparation

This notebook will read in source data, clean and convert datatypes, and filter data based on geospatial conditions.

 Read in source data includes:
* Permit data - includes specifications for new wells to be drilled by an operator
* Leasing data - includes bonus prices for active federal leases, grantee, acreage, effective date, etc.
* New production data - includes well and production data (total oil/gas produced) for wells drilled in last 4 years
* Old production data - older, historical well information
* Sale shapefile - includes geolocation and boundaries of each tract in the sale

Permit, leasing, and production data (oil/gas records) is batch downloaded from a subscribed service provided by Enervus.
Sale shapefile is found at sale auction site

Cleaning/Preparation process includes:
* Dropping fields that are not needed for evaluation.
* Conversion to a uniform CRS (coordinate reference system) to all geospatial data.
* Date fields converted to datetime objects
* Add fields **buffer and centroid**, which will create geospatial points to filter source oil/gas record data within defined radius
* Add fields for distance and cardinal direction of source data to sale tract centroid
* Export filtered data by tract to file for sale note and visual generation

##  2.  Sale Note Summaries and Figure Automation

This notebook will read in filtered data from export and write natural language summaries.  
The filtered data will also be used to create visualizations to be saved on PDF.

* Functions created in this book will write summaries for each stream of data (permit, production, and leasing activity)
* Functions will use basic statistical metrics like mean, mode, std. deviation to highlight/summarize the most pertinent information

## 3.  Machine Learning - Data Preparation

Read In Data:
1. Historical oil/gas prices - used to determine economics of wells throughout time
2. Training input data: permits, production within area of interest (AOI)
3. Training output data (response feature is bonus): leases

Establish full list of input variables as:
* Total Permits - total number of permits within 3 mile radius of lease during time training lease was taken
* Total Wells - total number of wells within 3 mile radius during time training lease was taken
* Avg First 6 Mo Oil - used to see how well wells performed in first 6 months of production
* Avg First 6 Mo Gas - used to see how well wells performed in first 6 months of production
* Qi Oil - used to see how well wells performed in first month of production
* Qi Gas - used to see how well wells performed in first month of production
* 6 Mo Oil Revenue $ - economic caluclation to see how much wells returned in 1st 6 months based on historical oil price
* 6 Mo Gas Rev $ - economic caluclation to see how much wells returned in 1st 6 months based on historical gas price
* Oil Price - oil price of a given year the training lease was taken
* Gas Price - gas price of a given year the training lease was taken

Develop function to filter data within 3 mile radius of each training lease and retrieve input variables laid out
Export training lease data with target variable and input variables


## 4. EDA and Cleaning for Training Data

1. EDA - Feature Selection
* Build scatter plots to analyze each predictor feature with response feature (bonus)
    * coloring by year lease was taken, we saw older leases did not correlate well with bonus price and oil revenue
* Generate univariate histograms for each feature
    *  log tranformation on the bonus feature helped demonstrate a normal bell curve due to high variance and magnitude differences within the data
* Correlation (Pearson vs Rank) plots helped distinguish higher correlation predictor features
    * highest absolute value of correlation were Total permits, total wells, 6 mo gas revenue, and 6 mo oil revenue
* Summary Statistics
    * Extremely high standard deviation and variance in data:  std. dev = 1426 | mean = 984
  

2. Cleaning Data Set
* Evaluated bonus prices where nulls occured on input features
    * built histogram to see distribution of bonus price on filtered dataset of null input features
    * Discovered leases with high bonuses and no wells or permits to justify this.  
    * Such leases would cause outliars in the dataset and skew the model.  Dropped outliars outside quantile 80%.
* Evaluated data where bonus prices were low but displayed strong productivity from oil revenue and rates
    * dropped leases based on qualitative analysis
* Drop older leases (older than 2007) due to uncorrelated behavior.
    * Technology and shale plays were not prolific within AOI before 2008. Therefore, low prices with acceptable revenue would not accurately reflect today's conditions and price action

## 5. Training and Testing Model (Linear and Tree) - Applied on Sales Results 
1. Preprocessing
* inputs and target variables were scaled using sklearn's standard scalar object

2. Feature Selection
* Logic/Experience was used to select features and corroborated with correlation coefficients 
* VIF (variance inflation factor) was performed to ensure multicolinearity was not heavily present on selected features initially chosen from correlation coefficients

3. MultiLinear Regression Model Analysis
* High MAE (mean absolute error) on testing data: MAE = 880 
    * explanation for such a large error is high variance in response variable and the nature of predicting value of asset in auction environment
    
* 80% of training data had percent errors less than 207% 
    * Hard to minimize as standard deviation in data is extremely high
    
* Percent error was respectable when bonuses were higher than $500/acre
    * The highest percent errors were in low bonus values where there was not much variance in the predictor features to help differentiate prices
    * Percent error in bonuses greater than $500/acre was 68% | Percent error in bonuses less than $500/acre was 298%

4. Decision Tree Model
* Ran charts showing MAE on varying levels and samples per leave
    * The most optimal model, one that does not overfit, while still producing an error under 400 appeared to be a model with 4 samples as minimum and 6-8 levels
* MAE less than multi-linear regression on test data: MAE = 541 (Tree) vs 880 (Multi Lineear Regreesion)

5.  Actual Sale Results vs Predictions
* Multilinear model: Percent Error: 136%, MAE 247
* Tree Model: Percent Error: 476%, MAE 623

* Explanation for better performance from the linear model, despite being the weaker model in the training/testing data, could be an overfit/rigid tree model
    * Tree models caluclate averages per leaf, which could cause high errors if mis-categorized

## 6.  Sale Template Automation - Inserting Meta Sale Data into Excel Spreadsheet and Automating Paperwork
1.  This script launches sale url and extracts the following data:
* Tract serial numbers
* Acreage/Size
* Legal description
• Downloads sale shapefile and moves it into respective sale folder

2.  After scraping data, the script will insert values into created sale template Excel spreadsheeting using openpyxl package

3.  After sale is complete, the script can execute a function to scrape the sale url to find bid amount based on company's bidder number.  The winning bid quantity is then automatically inputted into the sale spreadsheet to summarize capital spent
A
4. Finally, paperwork required to be submitted to federal government agency are filled in using field pdf template.  Fields required to be filled in are amount paid, total amount due, serial numbers, state, and date.
* Reference article for completing this task: https://bostata.com/how-to-populate-fillable-pdfs-with-python/

# Other Folders/Files
1.  GlobalFuncts_n_Vars.py contains functions and variables needed in multiple notebooks
2.  Data Folder - Folder for raw/source data
    * Training Data for Models: Permits, Production, Leases, Oil Prices, Gas Prices
    * Data for Sale Note Automation: Permits, Production, Old Production
3.  Output Data Folder - Folder for exported data
    * Sale tracts activity/filtered data (production, permits, leases around sale tracts)
    * Training leases activity/filtered data (production, permits)
    - Cleaned training data after EDA
4.  Results Folder - Folder for exported sale tract notes, visualizaiton pdf