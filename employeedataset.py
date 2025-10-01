import pandas as pd
import numpy as np



# Load your dataset
df = pd.read_csv("Employee.csv", encoding="latin1")
print(f"Original dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Basic data exploration
print(df.head(10))
print(f"\nData types:\n{df.dtypes}")

# Data cleaning
df.drop_duplicates(inplace=True)
df.reset_index(drop=True, inplace=True)
print(f"After removing duplicates: {df.shape}")

# Clean salary data
df['Annual_Salary_Clean'] = df['Annual Salary'].str.replace('$', '', regex=False)
df['Annual_Salary_Clean'] = df['Annual_Salary_Clean'].str.replace(',', '', regex=False)
df['Annual_Salary_Clean'] = pd.to_numeric(df['Annual_Salary_Clean'], errors='coerce')

# Remove null values
df = df.dropna(subset=['Annual_Salary_Clean'])
print(f"After cleaning salary data: {df.shape}")

# Create age groups
df['Age_Group'] = 'Unknown'
df.loc[df['Age'] < 30, 'Age_Group'] = 'Under 30'
df.loc[(df['Age'] >= 30) & (df['Age'] < 40), 'Age_Group'] = '30-39'
df.loc[(df['Age'] >= 40) & (df['Age'] < 50), 'Age_Group'] = '40-49'
df.loc[(df['Age'] >= 50) & (df['Age'] < 60), 'Age_Group'] = '50-59'
df.loc[df['Age'] >= 60, 'Age_Group'] = '60+'

# ==================== ANALYSIS AND VISUALIZATION ====================


print("SALARY STATISTICS")
salary_stats = df['Annual_Salary_Clean'].describe()
print(f"Count: {salary_stats['count']:,.0f} employees")
print(f"Mean: ${salary_stats['mean']:,.2f}")
print(f"Median: ${salary_stats['50%']:,.2f}")
print(f"Std Dev: ${salary_stats['std']:,.2f}")
print(f"Min: ${salary_stats['min']:,.2f}")
print(f"Max: ${salary_stats['max']:,.2f}")

# Department analysis
count_emp_dept = df.groupby('Department')['EEID'].count().sort_values(ascending=False)
print(f"\nEmployee count by department:")
for dept, count in count_emp_dept.items():
    print(f"  {dept}: {count}")

# Gender analysis
gender_counts = df['Gender'].value_counts()
print(f"\nGender distribution:")
for gender, count in gender_counts.items():
    print(f"  {gender}: {count} ({count/len(df)*100:.1f}%)")

# Experience level analysis
exp_level_counts = df['Exp lev'].value_counts()
print(f"\nExperience level distribution:")
for level, count in exp_level_counts.items():
    print(f"  {level}: {count} ({count/len(df)*100:.1f}%)")

# Age group analysis
age_group_counts = df['Age_Group'].value_counts()
print(f"\nAge group distribution:")
for age_group, count in age_group_counts.items():
    print(f"  {age_group}: {count} ({count/len(df)*100:.1f}%)")

# ==================== ADVANCED ANALYSIS ====================

# Department salary analysis
dept_avg_salary = df.groupby('Department')['Annual_Salary_Clean'].mean().sort_values(ascending=False)
print(f"\nAverage salary by department:")
for dept, salary in dept_avg_salary.items():
    print(f"  {dept}: ${salary:,.2f}")

# Top performers
top_performers = df.nlargest(10, 'Annual_Salary_Clean')
print(f"\nTop 10 highest paid employees:")
print("Rank | Employee ID | Department | Salary")
print("-" * 45)
for i, (_, emp) in enumerate(top_performers.iterrows(), 1):
    print(f"{i:^4} | {emp['EEID']:^11} | {emp['Department']:^10} | ${emp['Annual_Salary_Clean']:>9,.0f}")

# Pay gap analysis
# Simplified Pay gap analysis - No special characters
print("\n" + "="*50)
print("GENDER PAY GAP ANALYSIS")
print("="*50)

try:
    avg_salary_by_gender = df.groupby(['Department', 'Gender'])['Annual_Salary_Clean'].mean().reset_index()
    pivot_salary = avg_salary_by_gender.pivot(index='Department', columns='Gender', values='Annual_Salary_Clean')
    
    # Fill NaN values with 0 to avoid errors
    pivot_salary = pivot_salary.fillna(0)
    
    if 'Male' in pivot_salary.columns and 'Female' in pivot_salary.columns:
        pivot_salary['Pay_Gap'] = pivot_salary['Male'] - pivot_salary['Female']
        pivot_salary['Pay_Gap_Percentage'] = (pivot_salary['Pay_Gap'] / pivot_salary['Female'].replace(0, 1)) * 100
        
        print("Dept       | Male      | Female    | Gap       | Gap%")
        print("-" * 55)
        
        for dept in pivot_salary.index:
            male_sal = pivot_salary.loc[dept, 'Male']
            female_sal = pivot_salary.loc[dept, 'Female']
            gap = pivot_salary.loc[dept, 'Pay_Gap']
            gap_pct = pivot_salary.loc[dept, 'Pay_Gap_Percentage']
            
            # Safe printing with basic ASCII characters only
            print(f"{str(dept)[:10]:<10} | {male_sal:>8.0f} | {female_sal:>8.0f} | {gap:>8.0f} | {gap_pct:>5.1f}")
    
    else:
        print("Gender data incomplete - check CSV export for full analysis")
        
except Exception as e:
    print("Pay gap analysis will be available in CSV export")
    print("Error handled - continuing with other analyses")

# ==================== CSV EXPORT SECTION ====================


print(" EXPORTING ANALYSIS RESULTS TO CSV FILES")

# 1. Export main processed dataset
df.to_csv('employee_data_processed.csv', index=False)
print(" Main dataset exported to 'employee_data_processed.csv'")

# 2. Export department analysis
dept_analysis = df.groupby('Department').agg({
    'EEID': 'count',
    'Annual_Salary_Clean': ['mean', 'max', 'min', 'std']
}).round(2)
dept_analysis.columns = ['Employee_Count', 'Avg_Salary', 'Max_Salary', 'Min_Salary', 'Salary_StdDev']
dept_analysis.to_csv('department_analysis.csv')
print("Department analysis exported to 'department_analysis.csv'")

# 3. Export gender distribution
gender_distribution = df['Gender'].value_counts().reset_index()
gender_distribution.columns = ['Gender', 'Employee_Count']
gender_distribution['Percentage'] = (gender_distribution['Employee_Count'] / len(df) * 100).round(1)
gender_distribution.to_csv('gender_distribution.csv', index=False)
print("Gender distribution exported to 'gender_distribution.csv'")

# 4. Export experience level analysis
exp_analysis = df.groupby('Exp lev').agg({
    'EEID': 'count',
    'Annual_Salary_Clean': 'mean'
}).reset_index()
exp_analysis.columns = ['Experience_Level', 'Employee_Count', 'Average_Salary']
exp_analysis['Average_Salary'] = exp_analysis['Average_Salary'].round(2)
exp_analysis.to_csv('experience_analysis.csv', index=False)
print("Experience analysis exported to 'experience_analysis.csv'")

# 5. Export age group analysis
age_analysis = df.groupby('Age_Group').agg({
    'EEID': 'count',
    'Annual_Salary_Clean': 'mean'
}).reset_index()
age_analysis.columns = ['Age_Group', 'Employee_Count', 'Average_Salary']
age_analysis['Average_Salary'] = age_analysis['Average_Salary'].round(2)
age_analysis.to_csv('age_group_analysis.csv', index=False)
print("Age group analysis exported to 'age_group_analysis.csv'")

# 6. Export business unit analysis
business_analysis = df.groupby('Business Unit').agg({
    'EEID': 'count',
    'Annual_Salary_Clean': 'mean'
}).reset_index()
business_analysis.columns = ['Business_Unit', 'Employee_Count', 'Average_Salary']
business_analysis['Average_Salary'] = business_analysis['Average_Salary'].round(2)
business_analysis.to_csv('business_unit_analysis.csv', index=False)
print("Business unit analysis exported to 'business_unit_analysis.csv'")

# 7. Export country analysis
country_analysis = df.groupby('Country').agg({
    'EEID': 'count',
    'Annual_Salary_Clean': 'mean'
}).reset_index()
country_analysis.columns = ['Country', 'Employee_Count', 'Average_Salary']
country_analysis['Average_Salary'] = country_analysis['Average_Salary'].round(2)
country_analysis.to_csv('country_analysis.csv', index=False)
print("Country analysis exported to 'country_analysis.csv'")

# 8. Export top performers
top_performers_export = df.nlargest(20, 'Annual_Salary_Clean')[
    ['EEID', 'Full Name', 'Department', 'Job Title', 'Annual_Salary_Clean', 'Age', 'Experience']
]
top_performers_export.to_csv('top_performers.csv', index=False)
print("Top performers exported to 'top_performers.csv'")

# 9. Export job title salary analysis
job_title_analysis = df.groupby('Job Title').agg({
    'EEID': 'count',
    'Annual_Salary_Clean': ['mean', 'max', 'min']
}).round(2)
job_title_analysis.columns = ['Employee_Count', 'Avg_Salary', 'Max_Salary', 'Min_Salary']
job_title_analysis = job_title_analysis.sort_values('Avg_Salary', ascending=False)
job_title_analysis.to_csv('job_title_analysis.csv')
print("Job title analysis exported to 'job_title_analysis.csv'")

# 10. Export gender pay gap analysis
pivot_salary_export = pivot_salary.round(2)
pivot_salary_export.to_csv('gender_pay_gap_analysis.csv')
print("Gender pay gap analysis exported to 'gender_pay_gap_analysis.csv'")

# 11. Export summary statistics
summary_stats = pd.DataFrame({
    'Metric': ['Total_Employees', 'Avg_Salary', 'Median_Salary', 'Max_Salary', 'Min_Salary', 
               'Salary_StdDev', 'Male_Employees', 'Female_Employees'],
    'Value': [
        len(df),
        df['Annual_Salary_Clean'].mean(),
        df['Annual_Salary_Clean'].median(),
        df['Annual_Salary_Clean'].max(),
        df['Annual_Salary_Clean'].min(),
        df['Annual_Salary_Clean'].std(),
        len(df[df['Gender'] == 'Male']),
        len(df[df['Gender'] == 'Female'])
    ]
})
summary_stats['Value'] = summary_stats['Value'].round(2)
summary_stats.to_csv('summary_statistics.csv', index=False)
print("Summary statistics exported to 'summary_statistics.csv'")
print("\n" + "="*60)
print("ALL CSV EXPORTS COMPLETED SUCCESSFULLY!")
print("="*60)
print("Files created:")
print("1. employee_data_processed.csv - Main dataset")
print("2. department_analysis.csv - Department metrics")
print("3. gender_distribution.csv - Gender breakdown")
print("4. experience_analysis.csv - Experience level data")
print("5. age_group_analysis.csv - Age demographics")
print("6. business_unit_analysis.csv - Business unit metrics")
print("7. country_analysis.csv - Country-wise data")
print("8. top_performers.csv - Highest paid employees")
print("9. job_title_analysis.csv - Job title salary data")
print("10. gender_pay_gap_analysis.csv - Pay equity analysis")
print("11. summary_statistics.csv - Overall statistics")

