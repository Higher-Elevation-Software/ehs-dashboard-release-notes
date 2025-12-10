#!/bin/bash
SUMMARY="This pull request refactors how chemical amounts are calculated in several methods within app/lib/air_permit_data.rb to ensure consistency and correctness. The main change introduces a new helper method, resolve_constsum_amount, which prioritizes the high value from constsum if present and non-zero, otherwise falling back to amount. This adjustment impacts how chemical data is processed and formatted throughout the codebase.

Chemical amount calculation updates:

Introduced the resolve_constsum_amount helper method to consistently select the correct value from constsum, using high if available and non-zero, or falling back to amount. (app/lib/air_permit_data.rb)
Updated format_direct_chemical_data and fetch_and_format_chemrefinfo_chemical_data to use resolve_constsum_amount instead of directly accessing constsum.amount, ensuring correct chemical amount selection. (app/lib/air_permit_data.rb) [1] [2]
Emissions calculation clarification:

Removed redundant multiplication by constituent_percentage in process_chemical_points, clarifying that chem_record[:amount] already represents the constituent weight. (app/lib/air_permit_data.rb)"

./test-dispatch.sh "dashboard-api" "abc123d" "hes-601: ixed constum 'amount' multiplication issues" "$SUMMARY" "97"
