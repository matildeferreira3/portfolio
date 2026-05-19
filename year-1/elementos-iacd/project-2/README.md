# Data exploration and enrichment for supervised classification

## Project Description
This project develops a full data science pipeline for supervised classification using the ```Hepatocellular Carcinoma (HCC)``` dataset, collected at Coimbra Hospital and University Center (CHUC), Portugal.  

The pipeline includes:
- **Data Exploration:** Examine feature types, record counts, class distribution, missing values, outliers, irrelevant features, etc., supported with visualizations.  
- **Data Preprocessing:** Imputation of missing values, feature scaling, data transformation, feature engineering, and removal of redundant features. 
- **Data Modeling:** Building classification models (Decision Trees and KNN) to predict 1-year survivability (“lives” or “dies”). Additional classifiers were optional.  
- **Evaluation:** Compare models using metrics such as confusion matrix, ROC/AUC, precision, recall, accuracy. Visualizations are provided with Matplotlib and Seaborn.  
- **Interpretation:** Extract meaningful insights, explain model behavior, discuss preprocessing effects, and provide recommendations for future analysis.

## Authors
- Ana Matilde Ferreira  
- Catarina Aguiar  
- Maria Leonor Carvalho  

## Libraries
Install the required packages using pip:
```pip install pandas matplotlib seaborn scikit-learn imbalanced-learn numpy```

## Environment
- macOS Sonoma 14.4.1
- Windows 11
- Python 3.12.0

## How to Run
The project is delivered as a Jupyter Notebook. To run:
1. Open the notebook in Jupyter or VSCode.
2. Execute the cells sequentially to reproduce data exploration, preprocessing, modeling, evaluation, and visualizations.
