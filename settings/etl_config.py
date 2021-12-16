# File to hold relationship for table_names to create database and its associate file name keyword to pull correct file

# running sales in chronological order to circumvent issue
sales_to_run = ["BLM WY 3-24-20", "BLM WY 6-23-20", 'BLM MT 9-22-20', 'BLM UT 9-29-20', "BLM WY 12-15-20"]

# variable to replace records if exist, if false, existing recoreds will persist and no records will be updated
replaceExistingRecords = True

#absolute paths for sale folders and db config file
db_config_path = '/Users/Mishaun_Bhakta/Documents/Python & Projects/Projects/BLM Lease Evaluation and Automation/settings/dbconfig.ini'
sales_path = "/Users/Mishaun_Bhakta/Documents/Python & Projects/Projects/BLM Lease Evaluation and Automation/Sales"

#dictionary to pass paths, filenames, and parsing information
mappings = {
        'output_data': {
            'path': "Output Data/Sale Tracts Activity Data",
            'parseCols': None,
            'table_names_file_names': {'leases': 'Leases Around Sale Tracts.xlsx',
                'new_prod': 'NewProd Around Sale Tracts.xlsx',
                'old_prod': 'OldProd Around Sale Tracts.xlsx',
                'permits': 'Permits Around Sale Tracts.xlsx'}
    },
        'sale_notes': {
            'path': "Sale Template Automation",
            'parseCols': {'header': 6, "usecols": 'B:U'},
            'table_names_file_names': {'internal_notes': 'Sale Notes.xlsm'}
    },

        'automated_sale_notes': {
            'path': "Results",
            'parseCols': None,
            'table_names_file_names': {'automated_notes': 'Automated Activity Summary Notes.xlsx'}
        }
}
