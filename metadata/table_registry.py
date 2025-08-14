
MOCK_TABLE_METADATA = {
    "SAP_HANA": {
        "STAGING_FINANCE.MONTHLY_PNL": {
            "columns": ["MONTH", "REVENUE", "EXPENSES", "PROFIT_OR_LOSS", "P_L_STATUS"],
            "primary_key": []
        },
        "STAGING_FINANCE.EXPENSES": {
            "columns": ["EXPENSE_ID", "EMPLOYEE_NAME", "DEPARTMENT", "EXPENSE_TYPE", "EXPENSE_DATE", "AMOUNT", "APPROVAL_STATUS"],
            "primary_key": ["EXPENSE_ID"]
        },
        "STAGING_FINANCE.PROFIT_DATA": {
            "columns": ["SALE_ID", "SALE_DATE", "CUSTOMER_NAME", "PRODUCT", "QUANTITY", "UNIT_PRICE",
                        "TOTAL_AMOUNT", "COST_PRICE", "PROFIT", "PROFIT_MARGIN"],
            "primary_key": ["SALE_ID"]
        },
        "STAGING_FINANCE.BUDGETS": {
            "columns": ["DEPARTMENT", "MONTH", "BUDGET", "ACTUAL", "VARIANCE"],
            "primary_key": []
        },
        "STAGING_FINANCE.WITHHOLDING_TAX": {
            "columns": ["DOCUMENT_ID", "VENDOR_ID", "TAX_CODE", "TAX_PERCENTAGE", "TAX_AMOUNT", "POSTING_DATE"],
            "primary_key": ["DOCUMENT_ID"]
        }
    },
    "BIGQUERY": {
        "wmt-cill-dev.subledger_datacert.TBL_SALES_DATA": {
            "columns": ["Sale_ID", "Sale_Date", "Customer_Name", "Product", "Quantity", "Unit_Price", "Total_Amount"],
            "types": ["string", "date", "string", "string", "integer", "float", "float"],
            "primary_key": ["Sale_ID"]
        },
        "wmt-cill-dev.subledger_datacert.TBL_CUSTOMERS_DATA": {
            "columns": ["customer_id", "name", "loyalty_points", "signup_date"],
            "types": ["string", "string", "integer", "date"],
            "primary_key": ["customer_id"]
        }
    },
    "EXCEL": {
        "vendor_payments": {
            "columns": ["Vendor_ID", "Vendor_Name", "Invoice_Number", "Invoice_Date", "Payment_Date", "Invoice_Amount", "Payment_Status", "Category", "Related_Revenue", "Profit_or_Loss", "P_L_Status"],
            "primary_key": ["Invoice_Number"]
        },
        "fixed_assets": {
            "columns": ["Asset_ID", "Asset_Name", "Acquisition_Date", "Acquisition_Value", "Depreciation_Value", "Net_Book_Value"],
            "primary_key": ["Asset_ID"]
        }
    }
}

def get_metadata() -> dict:
    return MOCK_TABLE_METADATA

def get_metadata_source_tables(source: str) -> dict:
    return MOCK_TABLE_METADATA.get(source,{})
