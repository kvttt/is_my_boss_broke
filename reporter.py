import argparse
from datetime import date
import re
import requests


def extract_core_suffix(proj_num: str):
    match = re.match(r"^(?:\d+)?([A-Z0-9]+)-(\d+)$", proj_num)
    if match:
        core = re.sub(r'^\d+', '', match.group(1))
        suffix = int(match.group(2))
        return core, suffix
    else:
        return proj_num, 0


def search_nih_reporter(pi_first_name: str, pi_last_name: str, pi_institutions: list,
                        offset: int = 0, limit: int = 10) -> dict:
    api_url = "https://api.reporter.nih.gov/v2/projects/search"
    headers = {'Content-Type': 'application/json'}

    today_str = date.today().isoformat()  # e.g., "2025-04-11"

    payload = {
        "criteria": {
            "pi_names": [{
                "first_name": pi_first_name,
                "last_name": pi_last_name
            }],
            "org_names_exact_match": pi_institutions,
            "project_end_date": {
                "from_date": today_str,
                "to_date": ""
            }
        },
        "offset": offset,
        "limit": limit
    }

    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def format_cost(amount):
    try:
        return f"${amount:,.2f}"
    except (ValueError, TypeError):
        return "N/A"


def print_project_info(project: dict):
    # PI Name
    pi_info = project.get("principal_investigators", [])
    pi_names = []
    for pi in pi_info:
        first = pi.get("first_name", "").strip()
        last = pi.get("last_name", "").strip()
        if first or last:
            pi_names.append(f"{first} {last}".strip())
    pi_names_str = ", ".join(pi_names) if pi_names else "N/A"
    # Project Title
    title = project.get("project_title", "N/A")
    # Institution
    organization_info = project.get("organization", {})
    institution = organization_info.get("org_name", "N/A")
    # Admin IC
    admin_ic_obj = project.get("agency_ic_admin", {})
    admin_ic = admin_ic_obj.get("name", "N/A")
    admin_ic_abbr = admin_ic_obj.get("abbreviation", "N/A")
    # Funding IC
    funding_ic_obj = project.get("agency_ic_fundings", {})[0]
    funding_ic = funding_ic_obj.get("name", "N/A")
    funding_ic_abbr = funding_ic_obj.get("abbreviation", "N/A")
    # Fiscal Year
    fiscal_year = project.get("fy") or project.get("fiscal_year", "N/A")
    # Project Number
    project_number = project.get("project_num", "N/A")
    # Start and End Dates
    start_date = project.get("project_start_date", "N/A")
    end_date = project.get("project_end_date", "N/A")
    # Total, Direct, and Indirect Costs
    total_cost = format_cost(project.get("award_amount"))
    direct_cost = format_cost(project.get("direct_cost_amt"))
    indirect_cost = format_cost(project.get("indirect_cost_amt"))
    indirect_cost_pct = project.get("indirect_cost_amt") / project.get("direct_cost_amt") * 100
    # Print project information
    print("=" * 80)
    print(f"PI Name: {pi_names_str}")
    print(f"Project Title: {title}")
    print(f"Institution: {institution}")
    print(f"Admin IC: {admin_ic} ({admin_ic_abbr})")
    print(f"Funding IC: {funding_ic} ({funding_ic_abbr})")
    print(f"Fiscal Year: {fiscal_year}")
    print(f"Project Number: {project_number}")
    print(f"Start: {start_date}")
    print(f"End: {end_date}")
    print(f"Total Cost: {total_cost}")
    print(f"Direct Cost: {direct_cost}")
    print(f"Indirect Cost: {indirect_cost} ({indirect_cost_pct:.2f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="Search NIH RePORTER for projects with specified principal investigator and institution criteria."
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
    parser.add_argument(
        "--offset", "-o", type=int, default=0,
        help="Pagination offset (default: 0)."
    )
    parser.add_argument(
        "--limit", "-n", type=int, default=50,
        help="Number of records to retrieve (default: 50)."
    )
    args = parser.parse_args()

    pi_first_name = args.first
    pi_last_name = args.last
    pi_institutions = [institution.strip() for institution in args.institutions.split(",")]

    try:
        data = search_nih_reporter(pi_first_name, pi_last_name, pi_institutions, offset=0, limit=50)
        results = data.get("results", [])
        if not results:
            print("No projects found matching the criteria.")
        else:
            deduped_projects = {}
            for project in results:
                proj_num = project.get("project_num", "N/A")
                core, suffix = extract_core_suffix(proj_num)
                if core in deduped_projects:
                    stored_proj = deduped_projects[core]
                    stored_suffix = extract_core_suffix(stored_proj.get("project_num", "N/A"))[1]
                    if suffix > stored_suffix:
                        deduped_projects[core] = project
                else:
                    deduped_projects[core] = project
            for project in deduped_projects.values():
                print_project_info(project)
            print("=" * 80)
    except requests.exceptions.HTTPError as http_err:
        print("HTTP error occurred:", http_err)
    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    main()
