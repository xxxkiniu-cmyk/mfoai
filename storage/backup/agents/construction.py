from core.notifier import send
from core.logger import Logger

CONSTRUCTION_JOBS = [
    {
        "client": "Remont lazienki",
        "area_m2": 6.0,
        "materials_cost_per_m2": 350.0,
        "labor_cost_per_m2": 500.0
    },
    {
        "client": "Szpachlowanie salonu",
        "area_m2": 35.0,
        "materials_cost_per_m2": 40.0,
        "labor_cost_per_m2": 60.0
    }
]

def calculate_estimate(job):
    area = job["area_m2"]
    materials = area * job["materials_cost_per_m2"]
    labor = area * job["labor_cost_per_m2"]
    total = materials + labor
    return {"client": job["client"], "area_m2": area, "materials": materials, "labor": labor, "total": total}

def run_construction():
    estimates = []
    total_revenue = 0.0
    for job in CONSTRUCTION_JOBS:
        est = calculate_estimate(job)
        estimates.append(
            f"Zlecenie: {est['client']}
"
            f"- Powierzchnia: {est['area_m2']} m2
"
            f"- Materialy: {est['materials']} PLN
"
            f"- Robocizna: {est['labor']} PLN
"
            f"- Suma: {est['total']} PLN"
        )
        total_revenue += est["total"]
    report = "Kosztorysy:

" + "

".join(estimates) + f"

Laczna wartosc: {total_revenue} PLN"
    try:
        send("MFO.ai: Budownictwo", report, priority="default")
        Logger.log("construction", "SYSTEM", 0.1, "SUCCESS")
    except Exception as e:
        Logger.log("construction", "SYSTEM", 0.1, "ERROR", error=str(e))
    return report

if __name__ == "__main__":
    print(run_construction())
