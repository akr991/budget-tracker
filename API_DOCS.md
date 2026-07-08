# API Documentation

Base URL: /api

Authentication:
- POST /auth/register
- POST /auth/login
- Bearer token required for all other endpoints

Profile and settings:
- GET /profile
- GET /profile/settings
- PUT /profile/settings

Region modules (India/UAE):
- Income: GET/POST/PUT/DELETE /regions/{region}/incomes
- Income summaries: GET /regions/{region}/incomes/summary/monthly
- Income yearly: GET /regions/{region}/incomes/summary/yearly
- Expenses: GET/POST/DELETE /regions/{region}/expenses
- Loans: GET/POST/PUT/DELETE /regions/{region}/loans
- Loan summary: GET /regions/{region}/loans/summary
- Loan alerts: GET /regions/{region}/loans/alerts
- Loan details page data: GET /regions/{region}/loans/{loan_id}/details
- Loan EMI history: GET /regions/{region}/loans/{loan_id}/emi-history
- Mark EMI completed: POST /regions/{region}/loans/{loan_id}/mark-emi-completed
- Subscriptions: GET/POST/PUT/DELETE /regions/{region}/subscriptions
- Subscription details: GET /regions/{region}/subscriptions/{subscription_id}/details
- Subscription payment history: GET /regions/{region}/subscriptions/{subscription_id}/history
- Mark subscription paid: POST /regions/{region}/subscriptions/{subscription_id}/mark-paid
- Debts: GET/POST/DELETE /regions/{region}/debts
- Debt repayments: POST /regions/{region}/debts/{debt_id}/repayments
- Debt summary: GET /regions/{region}/debts/summary
- Investments: GET/POST/DELETE /regions/{region}/investments
- Investment trends: GET /regions/{region}/investments/trends
- Gold: GET/POST/DELETE /regions/{region}/gold
- Gold summary: GET /regions/{region}/gold/summary
- Gold live price (optional): GET /regions/{region}/gold/live-price
- Monthly summary: GET /regions/{region}/monthly-summary

Total net worth:
- GET /net-worth/summary

CSV export:
- GET /export/csv?region=india&module=incomes

Notifications:
- GET /notifications/monthly-summary

Interactive OpenAPI docs:
- GET /docs
- GET /redoc
