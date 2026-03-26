def predict_cascade(driver, node_id, depth=4):
    # Query Neo4j for downstream nodes
    with driver.session() as session:
        result = session.run("""
            MATCH path = (start {id: $id})-[:CONNECTS_TO*1..4]->(downstream)
            RETURN downstream.id, downstream.health_score, 
                   length(path) as hops,
                   relationships(path)[-1].weight as edge_weight
        """, id=node_id)
        
        cascade = []
        for record in result:
            hops = record['hops']
            base_prob = (1 - record['downstream']['health_score']/100)
            # Probability decays with distance
            prob = base_prob * (0.6 ** hops) * record['edge_weight']
            timeline = hops * 8  # rough days estimate
            cascade.append({
                "node_id": record['downstream']['id'],
                "probability": round(prob, 2),
                "timeline_days": timeline
            })
        
        return sorted(cascade, key=lambda x: -x['probability'])