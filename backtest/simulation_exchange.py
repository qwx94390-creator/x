class SimulationExchange:
    def execute(self, order: dict) -> dict:
        return {"status": "filled", **order}
