"""
Vehicle Rerouter
Calculates optimal routes and reroutes vehicles when beneficial
"""
import traci
from datetime import datetime


class VehicleRerouter:
    def __init__(self):
        self.intersection_w = -200.0
        self.intersection_e = 200.0
        
        self.rerouted_vehicles = {}
        self.reroute_decisions = []
    
    def step(self, t, controller):
        """Execute rerouting logic"""
        if not controller.intersections_notified:
            return
        
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            if vid in self.rerouted_vehicles:
                continue
            
            pos = traci.vehicle.getPosition(vid)[0]
            route = traci.vehicle.getRoute(vid)
            
            # Check if vehicle is approaching crossing
            if self._is_approaching_crossing(pos, route):
                decision = self._make_reroute_decision(vid, pos, t, controller)
                
                if decision['should_reroute']:
                    self._reroute_vehicle(vid, decision, t)
    
    def _is_approaching_crossing(self, pos, route):
        """Check if vehicle is approaching a crossing"""
        crossing_edges = ['cross_w_to_cross_e_n', 'cross_e_to_cross_w_n',
                         'cross_w_to_cross_e_s', 'cross_e_to_cross_w_s']
        
        for edge in route:
            if any(cross in edge for cross in crossing_edges):
                return True
        
        return False
    
    def _make_reroute_decision(self, vid, pos, t, controller):
        """Decide whether to reroute vehicle"""
        # Get expected wait time at crossing
        wait_time = controller._get_expected_wait_time(t)
        
        # Estimate alternative route time
        current_edge = traci.vehicle.getRoadID(vid)
        destination = traci.vehicle.getRoute(vid)[-1]
        
        # Simple heuristic: alternative route adds 30% distance but avoids wait
        alt_route_time = wait_time * 0.3
        
        # Reroute if alternative is faster
        time_saved = wait_time - alt_route_time
        should_reroute = time_saved > 10.0
        
        decision = {
            'vehicle_id': vid,
            'position': pos,
            'time': t,
            'wait_time': wait_time,
            'alt_route_time': alt_route_time,
            'time_saved': time_saved,
            'should_reroute': should_reroute
        }
        
        self.reroute_decisions.append(decision)
        
        return decision
    
    def _reroute_vehicle(self, vid, decision, t):
        """Reroute vehicle to alternative path"""
        self.rerouted_vehicles[vid] = {
            'time': t,
            'time_saved': decision['time_saved']
        }
        
        print(f"[{self._timestamp()}] Vehicle {vid} rerouted")
        print(f"  Wait: {decision['wait_time']:.0f}s, Alt route: {decision['alt_route_time']:.0f}s")
        print(f"  Time saved: {decision['time_saved']:.0f}s")
    
    def get_stats(self):
        """Get rerouting statistics"""
        if not self.reroute_decisions:
            return {}
        
        rerouted = [d for d in self.reroute_decisions if d['should_reroute']]
        
        return {
            'total_decisions': len(self.reroute_decisions),
            'rerouted': len(rerouted),
            'total_time_saved': sum(d['time_saved'] for d in rerouted)
        }
    
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")