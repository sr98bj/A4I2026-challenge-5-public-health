"""
Mock dataset and context isolation accessors for Fulton County, Georgia.
Enforces the context boundary between operational planning and equity auditing.
"""

from typing import List, Dict
from models import NeighborhoodCandidate, OperationalCandidate, EquityMetrics


FULTON_CANDIDATE_DATASET: List[NeighborhoodCandidate] = [
    NeighborhoodCandidate(
        operational=OperationalCandidate(
            tract_id="CT_13121008200",
            neighborhood_name="Bankhead / West Lake",
            intersection="Donald Lee Hollowell Pkwy NW & Anderson Ave NW",
            quadrant="Westside",
            latitude=33.7712,
            longitude=-84.4532,
            parking_capacity_spots=14,
            surface_type="paved lot",
            permit_required=False,
            foot_traffic_level="High",
            operational_notes="Spacious church parking lot with wide ingress/egress. Van turning radius accommodated easily; level asphalt."
        ),
        equity=EquityMetrics(
            uninsured_rate_pct=28.4,
            poverty_rate_pct=32.1,
            transit_travel_time_to_care_min=52.0,
            bus_transfers_required=2,
            dist_to_safety_net_clinic_miles=4.8,
            dist_to_general_clinic_miles=2.1,
            safety_net_desert=True,
            composite_vulnerability_index=0.89
        )
    ),
    NeighborhoodCandidate(
        operational=OperationalCandidate(
            tract_id="CT_13121003600",
            neighborhood_name="Vine City / English Avenue",
            intersection="Joseph E Boone Blvd NW & Sunset Ave NW",
            quadrant="Westside",
            latitude=33.7634,
            longitude=-84.4095,
            parking_capacity_spots=10,
            surface_type="paved lot",
            permit_required=False,
            foot_traffic_level="High",
            operational_notes="Community center lot with direct street sidewalk ramp. High pedestrian visibility."
        ),
        equity=EquityMetrics(
            uninsured_rate_pct=26.1,
            poverty_rate_pct=34.5,
            transit_travel_time_to_care_min=38.0,
            bus_transfers_required=1,
            dist_to_safety_net_clinic_miles=2.2,
            dist_to_general_clinic_miles=1.9,
            safety_net_desert=False,
            composite_vulnerability_index=0.84
        )
    ),
    NeighborhoodCandidate(
        operational=OperationalCandidate(
            tract_id="CT_13121010300",
            neighborhood_name="South Fulton / Old National",
            intersection="Old National Hwy & Flat Shoals Rd",
            quadrant="South Fulton",
            latitude=33.6190,
            longitude=-84.4780,
            parking_capacity_spots=22,
            surface_type="paved lot",
            permit_required=False,
            foot_traffic_level="High",
            operational_notes="Shopping center peripheral apron. Exceptional space for van generator and waiting canopy."
        ),
        equity=EquityMetrics(
            uninsured_rate_pct=24.8,
            poverty_rate_pct=23.0,
            transit_travel_time_to_care_min=68.0,
            bus_transfers_required=3,
            dist_to_safety_net_clinic_miles=11.2,
            dist_to_general_clinic_miles=3.4,
            safety_net_desert=True,
            composite_vulnerability_index=0.86
        )
    ),
    NeighborhoodCandidate(
        operational=OperationalCandidate(
            tract_id="CT_13121007805",
            neighborhood_name="Adamsville / MLK Jr Dr",
            intersection="Martin Luther King Jr Dr SW & Delmar Ln NW",
            quadrant="Westside",
            latitude=33.7548,
            longitude=-84.4981,
            parking_capacity_spots=16,
            surface_type="paved lot",
            permit_required=False,
            foot_traffic_level="Moderate",
            operational_notes="Municipal recreation center lot. Restroom facilities accessible for medical staff."
        ),
        equity=EquityMetrics(
            uninsured_rate_pct=22.5,
            poverty_rate_pct=26.2,
            transit_travel_time_to_care_min=58.0,
            bus_transfers_required=2,
            dist_to_safety_net_clinic_miles=7.6,
            dist_to_general_clinic_miles=2.5,
            safety_net_desert=True,
            composite_vulnerability_index=0.79
        )
    ),
    NeighborhoodCandidate(
        operational=OperationalCandidate(
            tract_id="CT_13121010800",
            neighborhood_name="College Park / Main St",
            intersection="Main St & Harvard Ave",
            quadrant="South Fulton",
            latitude=33.6534,
            longitude=-84.4491,
            parking_capacity_spots=12,
            surface_type="asphalt",
            permit_required=True,
            foot_traffic_level="Moderate",
            operational_notes="Depot square parking spaces. Requires municipal weekend parking permit notification."
        ),
        equity=EquityMetrics(
            uninsured_rate_pct=21.0,
            poverty_rate_pct=24.8,
            transit_travel_time_to_care_min=46.0,
            bus_transfers_required=2,
            dist_to_safety_net_clinic_miles=8.9,
            dist_to_general_clinic_miles=1.8,
            safety_net_desert=True,
            composite_vulnerability_index=0.75
        )
    ),
    NeighborhoodCandidate(
        operational=OperationalCandidate(
            tract_id="CT_13121005501",
            neighborhood_name="Pittsburgh / Mechanicsville",
            intersection="McDaniel St SW & University Ave SW",
            quadrant="South Atlanta",
            latitude=33.7225,
            longitude=-84.4010,
            parking_capacity_spots=10,
            surface_type="paved lot",
            permit_required=False,
            foot_traffic_level="High",
            operational_notes="Community center lot alongside public greenspace. Strong pedestrian visibility."
        ),
        equity=EquityMetrics(
            uninsured_rate_pct=25.2,
            poverty_rate_pct=31.0,
            transit_travel_time_to_care_min=35.0,
            bus_transfers_required=1,
            dist_to_safety_net_clinic_miles=2.4,
            dist_to_general_clinic_miles=1.5,
            safety_net_desert=False,
            composite_vulnerability_index=0.81
        )
    ),
    NeighborhoodCandidate(
        operational=OperationalCandidate(
            tract_id="CT_13121001900",
            neighborhood_name="Peachtree Center / Downtown",
            intersection="Peachtree St NE & Ellis St NE",
            quadrant="Central Atlanta",
            latitude=33.7588,
            longitude=-84.3879,
            parking_capacity_spots=6,
            surface_type="curb",
            permit_required=True,
            foot_traffic_level="High",
            operational_notes="Designated municipal curb staging near rail entrance. High foot traffic, tight vehicle clearance."
        ),
        equity=EquityMetrics(
            uninsured_rate_pct=11.2,
            poverty_rate_pct=14.5,
            transit_travel_time_to_care_min=12.0,
            bus_transfers_required=0,
            dist_to_safety_net_clinic_miles=0.6,
            dist_to_general_clinic_miles=0.3,
            safety_net_desert=False,
            composite_vulnerability_index=0.31
        )
    ),
    NeighborhoodCandidate(
        operational=OperationalCandidate(
            tract_id="CT_13121009502",
            neighborhood_name="Midtown / Piedmont Park",
            intersection="10th St NE & Piedmont Ave NE",
            quadrant="Central Atlanta",
            latitude=33.7825,
            longitude=-84.3789,
            parking_capacity_spots=35,
            surface_type="paved lot",
            permit_required=True,
            foot_traffic_level="High",
            operational_notes="Extremely spacious paved park lot. Easy turnaround, electrical hookups available. Ideal parking logistics."
        ),
        equity=EquityMetrics(
            uninsured_rate_pct=5.4,
            poverty_rate_pct=8.2,
            transit_travel_time_to_care_min=14.0,
            bus_transfers_required=0,
            dist_to_safety_net_clinic_miles=2.8,
            dist_to_general_clinic_miles=0.4,
            safety_net_desert=False,
            composite_vulnerability_index=0.15
        )
    ),
    NeighborhoodCandidate(
        operational=OperationalCandidate(
            tract_id="CT_13121010115",
            neighborhood_name="Buckhead Forest",
            intersection="Peachtree Rd NE & Piedmont Rd NE",
            quadrant="North Fulton",
            latitude=33.8431,
            longitude=-84.3685,
            parking_capacity_spots=40,
            surface_type="paved lot",
            permit_required=False,
            foot_traffic_level="Moderate",
            operational_notes="Sprawling commercial plaza with oversized stalls and zero parking fees. Effortless vehicle access."
        ),
        equity=EquityMetrics(
            uninsured_rate_pct=4.1,
            poverty_rate_pct=5.0,
            transit_travel_time_to_care_min=15.0,
            bus_transfers_required=0,
            dist_to_safety_net_clinic_miles=7.1,
            dist_to_general_clinic_miles=0.2,
            safety_net_desert=False,
            composite_vulnerability_index=0.08
        )
    ),
    NeighborhoodCandidate(
        operational=OperationalCandidate(
            tract_id="CT_13121011422",
            neighborhood_name="Sandy Springs South",
            intersection="Roswell Rd & Hammond Dr",
            quadrant="North Fulton",
            latitude=33.9212,
            longitude=-84.3792,
            parking_capacity_spots=28,
            surface_type="paved lot",
            permit_required=False,
            foot_traffic_level="Moderate",
            operational_notes="Public library lot with smooth asphalt and accessible wheelchair ramps. Ample staff shade."
        ),
        equity=EquityMetrics(
            uninsured_rate_pct=7.8,
            poverty_rate_pct=6.9,
            transit_travel_time_to_care_min=18.0,
            bus_transfers_required=0,
            dist_to_safety_net_clinic_miles=12.0,
            dist_to_general_clinic_miles=0.5,
            safety_net_desert=False,
            composite_vulnerability_index=0.18
        )
    ),
]


# ---------------------------------------------------------------------------
# Strict Context Isolation Accessor Functions
# ---------------------------------------------------------------------------

def get_operational_candidates() -> List[OperationalCandidate]:
    """CONTEXT BARRIER ENFORCEMENT:
    Returns exclusively physical parking and operational candidate data.
    All equity, uninsured, poverty, and clinic distance metrics are completely stripped.
    This is the ONLY data function accessible to Agent 1 (Planner).
    """
    return [candidate.operational.model_copy(deep=True) for candidate in FULTON_CANDIDATE_DATASET]


def get_equity_data_lookup() -> Dict[str, EquityMetrics]:
    """RESTRICTED ACCESSOR:
    Returns demographic, economic, and clinic accessibility metrics keyed by tract_id.
    STRICTLY DENIED to Agent 1. Permitted ONLY to Agent 2 (Auditor) and Evaluator.
    """
    return {
        candidate.operational.tract_id: candidate.equity.model_copy(deep=True)
        for candidate in FULTON_CANDIDATE_DATASET
    }


def get_full_candidates_lookup() -> Dict[str, NeighborhoodCandidate]:
    """Full candidate lookup for system synthesizer."""
    return {
        candidate.operational.tract_id: candidate.model_copy(deep=True)
        for candidate in FULTON_CANDIDATE_DATASET
    }
