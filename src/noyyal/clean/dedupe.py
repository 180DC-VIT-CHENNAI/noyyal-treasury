def drop_statement_duplicates(frame): return frame.drop_duplicates(subset=[x for x in frame.columns if x!='txn_id']).sort_values(['value_date','txn_id']).reset_index(drop=True)
