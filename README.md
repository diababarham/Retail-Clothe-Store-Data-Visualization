# Retail-Clothe-Store-Data-Visualization
This is a project that is built with Power Bi to visualize data of a clothing retail store. The data used is generated on python with a planned database schema in place.

Since I could not find a suitable public dataset that matched the requirements for the intended visuals, I created a custom database with python and designed the data tables. All data in this repository is randomly generated and can be freely used for any retail analytics, data modeling, or Power BI practice project.

The data does not represent any company, the name H&M is used as an example retail company rather than data based off of their work.

# Database Structure
The database follows a star schema design with fact and dimension tables.

# Fact Tables
-factSales  
   Contains individual transaction records including date, store, product, customer, quantity, and revenue.  
-factInventory  
   Tracks daily stock levels for each product at each store.  
-factFinancials  
   Contains daily financial performance per store, including revenue, cost of goods sold (COGS), expenses, taxes, and net profit.  

# Dimension Tables
-dimProduct  
   Product details (product name, category, subcategory, brand, unit price, etc.).  
-dimDate  
   Date dimension covering the period from January 1, 2024 to March 30, 2026.  
-dimStore  
   Branch information (store name, location, region, city, etc.) – all stores are located in the UAE.  
-dimCustomer  
  Customer information (customer ID, name, age group, gender, location, customer segment, etc.).  

 # The schema
<img width="945" height="598" alt="image" src="https://github.com/user-attachments/assets/6c91bd52-8017-40e2-949e-ce06dd500526" />
<img width="940" height="545" alt="image" src="https://github.com/user-attachments/assets/edf6b7c7-1af7-4039-bac3-3d7d6c5c1447" />
