# Database Schema

## users
- id (PK)
- email (unique)
- full_name
- hashed_password
- is_active
- created_at

## user_settings
- id (PK)
- user_id (FK -> users.id, unique)
- dark_mode
- monthly_summary_notifications

## income_entries
- id (PK)
- user_id (FK -> users.id)
- region (india|uae)
- category (salary|business|rental|other)
- amount
- entry_date
- notes
- created_at

## expense_entries
- id (PK)
- user_id (FK -> users.id)
- region
- category
- amount
- entry_date
- notes
- created_at

## loans
- id (PK)
- user_id (FK -> users.id)
- region
- loan_name
- emi_amount
- emi_date (day of month when EMI is due)
- remaining_months
- interest_rate (nullable)
- start_date (nullable)
- created_at

## loan_emi_history
- id (PK)
- loan_id (FK -> loans.id)
- month
- year
- status (completed|pending)
- completed_at (nullable)
- created_at

## debts
- id (PK)
- user_id (FK -> users.id)
- region
- lender_name
- amount
- due_date
- notes
- created_at

## debt_repayments
- id (PK)
- debt_id (FK -> debts.id)
- amount
- payment_date

## investments
- id (PK)
- user_id (FK -> users.id)
- region
- name
- investment_type (mutual_fund|stocks|sip|fd|nps|crypto|other)
- invested_value
- current_value
- entry_date
- created_at

## gold_holdings
- id (PK)
- user_id (FK -> users.id)
- region
- quantity
- unit (grams|sovereigns)
- price_per_gram
- entry_date
- created_at

## subscriptions
- id (PK)
- user_id (FK -> users.id)
- region
- subscription_name
- monthly_cost
- billing_date (day of month)
- category
- notes (nullable)
- created_at

## subscription_payment_history
- id (PK)
- subscription_id (FK -> subscriptions.id)
- month
- year
- status (paid|pending)
- paid_at (nullable)
- created_at
