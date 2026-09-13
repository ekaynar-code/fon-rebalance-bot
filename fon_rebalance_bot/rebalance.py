"""
Portföy ağırlıklarını hesaplar ve 5/25 kuralına göre rebalancing sinyali üretir.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FundStatus:
    code: str
    name: str
    price: float
    units: float
    value: float
    current_weight: float
    target_weight: float
    deviation_pct_points: float  # yüzde puan cinsinden sapma (current - target)
    needs_rebalance: bool
    suggested_action: str  # "AL", "SAT", "-"
    suggested_amount_try: float  # önerilen işlem tutarı (TL), yönsüz (mutlak)


def evaluate_portfolio(
    funds_with_prices: list[dict],
    cash_balance_try: float,
    cash_target_weight: float,
    abs_threshold_pct: float,
    rel_threshold_pct: float,
) -> tuple[list[FundStatus], float]:
    """
    funds_with_prices: [{"code", "name", "price", "units", "target_weight"}, ...]
    Dönüş: (fon_durumlari, toplam_portfoy_degeri)
    """
    fund_values = []
    for f in funds_with_prices:
        value = f["price"] * f["units"]
        fund_values.append({**f, "value": value})

    total_value = sum(f["value"] for f in fund_values) + cash_balance_try
    if total_value <= 0:
        raise ValueError(
            "Toplam portföy değeri sıfır veya negatif görünüyor. "
            "config.yaml içindeki 'units' alanlarını doldurdun mu?"
        )

    statuses: list[FundStatus] = []
    for f in fund_values:
        current_weight = f["value"] / total_value
        target_weight = f["target_weight"]
        deviation = current_weight - target_weight  # işaretli: pozitifse fazla, negatifse eksik
        deviation_pct_points = deviation * 100

        abs_dev = abs(deviation_pct_points)
        rel_limit = target_weight * 100 * (rel_threshold_pct / 100)
        epsilon = 1e-9  # kayan nokta yuvarlama hatalarını tolere et
        needs_rebalance = (
            abs_dev >= abs_threshold_pct - epsilon
            or abs_dev >= rel_limit - epsilon
        )

        if needs_rebalance:
            # Hedefe dönmek için gereken TL tutarı
            target_value = target_weight * total_value
            diff_value = f["value"] - target_value  # pozitifse fazla var -> SAT
            suggested_action = "SAT" if diff_value > 0 else "AL"
            suggested_amount = abs(diff_value)
        else:
            suggested_action = "-"
            suggested_amount = 0.0

        statuses.append(
            FundStatus(
                code=f["code"],
                name=f.get("name", f["code"]),
                price=f["price"],
                units=f["units"],
                value=f["value"],
                current_weight=current_weight,
                target_weight=target_weight,
                deviation_pct_points=deviation_pct_points,
                needs_rebalance=needs_rebalance,
                suggested_action=suggested_action,
                suggested_amount_try=suggested_amount,
            )
        )

    return statuses, total_value
