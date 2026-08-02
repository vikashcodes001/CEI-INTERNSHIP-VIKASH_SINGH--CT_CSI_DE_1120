# E-Commerce Shopping Dataset Analysis

Exploratory Data Analysis (EDA), data cleaning, feature engineering, and visual analysis on e-commerce product listings.

## Repository Structure

```
shopping-analysis/
│── data/
│   └── combined_dataset.csv
│── notebook/
│   └── analysis.ipynb
│── README.md
```

## Dataset Overview

The dataset (`combined_dataset.csv`) contains product-level information collected across various shopping categories. Key variables include:
- `product_id`: Unique identifier for each product.
- `title`: Product title / brand name.
- `product_description`: Textual summary of the item.
- `initial_price`: Original list price before discounts.
- `final_price`: Discounted price in Indian Rupees (₹).
- `discount`: Discount percentage applied.
- `rating`: Customer rating score (1.0 - 5.0).
- `ratings_count`: Total number of customer reviews.
- `category`: Product grouping (e.g., backpacks, watches, yoga mats).

## Steps & Analysis Workflow

1. **Load Data**: Import core analytics packages (`pandas`, `numpy`, `matplotlib`, `seaborn`), load `combined_dataset.csv`, and inspect shape and columns.
2. **Understand Data**: Analyze data types, missing value distributions, and general summary statistics via `.info()` and `.describe()`.
3. **Data Cleaning**: Clean currency symbols from `final_price`, cast numerical attributes to appropriate numeric types, impute missing discount rates based on initial/final price, and remove duplicate product records.
4. **Feature Engineering**:
   - `price_difference`: Absolute savings amount (`initial_price - final_price`).
   - `popularity_metric`: Composite score combining rating and logarithmic review count (`rating * log1p(ratings_count)`).
   - `savings_percentage`: Effective discount percentage.
5. **Analysis**:
   - **Univariate Analysis**: Statistical distribution of prices, ratings, and discounts.
   - **Bivariate Analysis**: Relationships and correlation matrix between pricing, discounts, and customer engagement metrics.
   - **Category-level Analysis**: Grouped aggregations detailing average prices, ratings, review volume, and popularity scores by category.
6. **Visualization**: Comprehensive multi-panel plots including histograms, boxplots, category bar charts, and feature correlation heatmaps.
7. **Insights & Business Implications**: Actionable key findings detailing pricing strategies, promotional optimization, and catalog management recommendations.

## Key Insights

- **Price Sensitivity**: The majority of products are concentrated in affordable to mid-tier price ranges. Significant discounts heavily influence customer review counts.
- **Popularity Isolation**: Log-scaled review weighting isolates high-volume flagship items from products with inflated ratings based on single reviews.
- **Category Leadership**: Categories such as backpacks, watches, and home goods drive top transaction volume and review engagement.

## How to Run

1. Open `notebook/analysis.ipynb` in Jupyter Notebook or VS Code.
2. Ensure required dependencies are installed:
   ```bash
   pip install pandas numpy matplotlib seaborn
   ```
3. Run all cells sequentially.
