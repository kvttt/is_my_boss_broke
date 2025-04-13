import argparse
from datetime import datetime, date
import requests

TODAY = date.today()


def search_nih(pi_first_name: str, pi_last_name: str, pi_institutions: list) -> dict:
    api_url = "https://api.reporter.nih.gov/v2/projects/search"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "criteria": {
            "pi_names": [{"first_name": pi_first_name, "last_name": pi_last_name}],
            "org_names": pi_institutions,
            "project_end_date": {"from_date": TODAY.isoformat(), "to_date": ""}
        },
        "offset": 0,
        "limit": 10,
    }
    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def search_nsf(pi_first_name: str, pi_last_name: str, pi_institutions: list) -> dict:
    url = f"https://api.nsf.gov/services/v1/awards.json"
    params = {
        'pdPIName': f'"{pi_first_name}+{pi_last_name}"',
        'awardeeName': pi_institutions,
        'expDateStart': TODAY.strftime('%m/%d/%Y'),
        'printFields': 'id,agency,awardeeName,coPDPI,pdPIName,startDate,expDate,estimatedTotalAmt,fundsObligatedAmt,title',
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def format_cost(amount: int) -> str:
    return f"${amount:,.2f}"


def format_nih_date(date_str: str) -> str:
    dt = datetime.strptime(date_str.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
    return dt.strftime("%B %d, %Y %I:%M %p")


def format_nsf_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%m/%d/%Y")
    return dt.strftime("%B %d, %Y")


def print_nih_project_info(response: dict):
    for project in response.get("results", []):
        pi_lst = project.get("principal_investigators", [])
        pi_names = [f"{pi.get('first_name', '').strip()} {pi.get('last_name', '').strip()}" for pi in pi_lst]
        pi_names_str = ", ".join(pi_names)
        title = project.get("project_title", "N/A")
        organization = project.get("organization", {}).get("org_name", "N/A")
        admin_ic = project.get("agency_ic_admin", {}).get("name", "N/A")
        admin_ic_abbr = project.get("agency_ic_admin", {}).get("abbreviation", "N/A")
        funding_ic = project.get("agency_ic_fundings", [{}])[0].get("name", "N/A")
        funding_ic_abbr = project.get("agency_ic_fundings", [{}])[0].get("abbreviation", "N/A")
        fiscal_year = project.get("fiscal_year", "N/A")
        project_number = project.get("project_num", "N/A")
        start_date = format_nih_date(project.get("project_start_date", "N/A"))
        end_date = format_nih_date(project.get("project_end_date", "N/A"))
        total_cost = format_cost(int(project.get("award_amount")))
        direct_cost = format_cost(int(project.get("direct_cost_amt")))
        indirect_cost = format_cost(int(project.get("indirect_cost_amt")))
        indirect_cost_pct = project.get("indirect_cost_amt") / project.get("direct_cost_amt") * 100
        print("=" * 80)
        print(f"PI Name: {pi_names_str}")
        print(f"Project Title: {title}")
        print(f"Organization: {organization}")
        print(f"Admin IC: {admin_ic} ({admin_ic_abbr})")
        print(f"Funding IC: {funding_ic} ({funding_ic_abbr})")
        print(f"Fiscal Year: {fiscal_year}")
        print(f"Project Number: {project_number}")
        print(f"Start: {start_date}")
        print(f"End: {end_date}")
        print(f"Total Cost: {total_cost}")
        print(f"Direct Cost: {direct_cost}")
        print(f"Indirect Cost: {indirect_cost} ({indirect_cost_pct:.2f}%)")


def print_nsf_project_info(response: dict):
    for project in response.get("response", {}).get("award", []):
        pi_lst = project.get("coPDPI", [])
        pi_lst.append(project.get("pdPIName", ""))
        pi_names_str = ", ".join(pi_lst)
        title = project.get("title", "N/A")
        organization = project.get("awardeeName", "N/A")
        agency = project.get("agency", "N/A")
        project_number = project.get("id", "N/A")
        start_date = format_nsf_date(project.get("startDate", "N/A"))
        end_date = format_nsf_date(project.get("expDate", "N/A"))
        estimated_total_amt = format_cost(int(project.get("estimatedTotalAmt")))
        funds_obligated_amt = format_cost(int(project.get("fundsObligatedAmt")))
        print("=" * 80)
        print(f"PI Name: {pi_names_str}")
        print(f"Project Title: {title}")
        print(f"Organization: {organization}")
        print(f"Agency: {agency}")
        print(f"Project Number: {project_number}")
        print(f"Start: {start_date}")
        print(f"End: {end_date}")
        print(f"Estimated Total Amount: {estimated_total_amt}")
        print(f"Funds Obligated Amount: {funds_obligated_amt}")


def main():
    parser = argparse.ArgumentParser(
        description="Search NIH RePORTER and NSF for projects with specified principal investigator and institution criteria."
    )
    parser.add_argument(
        "--first", "-f", required=True,
        help="Exact first name of the principal investigator."
    )
    parser.add_argument(
        "--last", "-l", required=True,
        help="Exact last name of the principal investigator."
    )
    parser.add_argument(
        "--institutions", "-i", required=True,
        help="Comma-separated list of institution names (exact matches)."
    )
    args = parser.parse_args()

    pi_first_name = args.first
    pi_last_name = args.last
    pi_institutions = [institution.strip() for institution in args.institutions.split(",")]

    nih_res = search_nih(pi_first_name, pi_last_name, pi_institutions)
    nsf_res = search_nsf(pi_first_name, pi_last_name, pi_institutions)

    print_nih_project_info(nih_res)
    print_nsf_project_info(nsf_res)

    print("=" * 80)


if __name__ == "__main__":
    main()
