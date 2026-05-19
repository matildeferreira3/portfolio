# Gradient Boosting for Class Imbalance in Binary Classification

## Learning Goals
1. Understand how a selected Machine Learning (ML) algorithm works in detail, both theoretically and empirically.
2. Understand how benchmarking of ML algorithms is carried out.
3. Understand the difference between ML research and the use of ML to solve a specific application.

## Objective
The goal of this project is to implement a Gradient Boosting classifier from scratch and evaluate its performance on datasets with class imbalance. Two approaches were explored to improve performance under class imbalance:

1. **Weighted Loss Function:** Modify the loss function to assign different weights to each class.  
2. **Controlled Tree Diversity:** Modify the algorithm to control the diversity of the base decision trees.

## Description
Gradient Boosting is a powerful ensemble method that iteratively builds decision trees to minimize a loss function. Real-world datasets often present challenges such as class imbalance, which can reduce model performance. This project addresses this challenge by implementing two modified versions of Gradient Boosting and benchmarking them on imbalanced binary classification datasets.

## Libraries
Install Python (3.9+) and the required packages:
- numpy  
- scipy  
- pandas  
- scikit-learn  
- plotly  
- seaborn  
- matplotlib  
- joblib

## How to Run
Open `assignment.ipynb` in Jupyter Notebook (or JupyterLab) and run all cells. 
Datasets are placed in the `dados/` folder.
