from dataclasses import dataclass


@dataclass
class DailyReport:
    day: str
    pnl: float
    volume: float
    fills: int
    signals: int
    rejected: int
    avg_edge_bps: float
    reason: str


class DailyReporter:
    @staticmethod
    def analyze_reason(report: dict) -> str:
        pnl = report.get("daily_realized_pnl", 0.0)
        rejected = report.get("rejected", 0)
        signals = report.get("signals", 0)
        avg_edge_bps = report.get("avg_edge_bps", 0.0)

        reasons: list[str] = []
        if signals == 0:
            reasons.append("无有效信号，策略处于观望")
        if rejected > 0:
            reasons.append(f"风控拒单 {rejected} 次，限制了成交")
        if avg_edge_bps < 60:
            reasons.append("平均价差偏低，套利空间不足")
        elif avg_edge_bps > 120:
            reasons.append("平均价差较高，信号质量较好")

        if pnl >= 0:
            reasons.append("总体盈利主要来自成交后的价差收益")
        else:
            reasons.append("总体亏损可能来自信号质量下降或成交成本放大")

        return "；".join(reasons)

    def build_report(self, day: str, snapshot: dict) -> DailyReport:
        return DailyReport(
            day=day,
            pnl=float(snapshot.get("daily_realized_pnl", 0.0)),
            volume=float(snapshot.get("volume", 0.0)),
            fills=int(snapshot.get("fills", 0)),
            signals=int(snapshot.get("signals", 0)),
            rejected=int(snapshot.get("rejected", 0)),
            avg_edge_bps=float(snapshot.get("avg_edge_bps", 0.0)),
            reason=self.analyze_reason(snapshot),
        )

    @staticmethod
    def render_message(report: DailyReport, llm_advice: str) -> str:
        return (
            f"日报 {report.day}\n"
            f"PnL: {report.pnl:.4f} USDT\n"
            f"Volume: {report.volume:.4f}\n"
            f"Fills/Signals/Rejected: {report.fills}/{report.signals}/{report.rejected}\n"
            f"AvgEdge: {report.avg_edge_bps:.2f} bps\n"
            f"原因分析: {report.reason}\n"
            f"LLM诊断建议:\n{llm_advice}"
        )
