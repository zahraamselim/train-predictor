import traci
from simulation.utils.logger import Logger
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class VehicleRerouter:
    """Calculate optimal routes and reroute vehicles"""
    
    def __init__(self):
        self.intersection_w = -200.0
        self.intersection_e = 200.0
        
        self.rerouted_vehicles = {}
        self.reroute_decisions = []
    
    def step(self, t, controller):
        if not controller.intersections_notified:
            return
        
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower() or vid in self.rerouted_vehicles:
                continue
            
            pos = traci.vehicle.getPosition(vid)[0]
            route = traci.vehicle.getRoute(vid)
            
            if self._is_approaching_crossing(route):
                decision = self._make_reroute_decision(vid, pos, t, controller)
                
                if decision['should_reroute']:
                    self._reroute_vehicle(vid, decision)
    
    def _is_approaching_crossing(self, route):
        crossing_edges = ['cross_w_to_cross_e_n', 'cross_e_to_cross_w_n',
                         'cross_w_to_cross_e_s', 'cross_e_to_cross_w_s']
        return any(any(cross in edge for cross in crossing_edges) for edge in route)
    
    def _make_reroute_decision(self, vid, pos, t, controller):
        wait_time = controller._get_expected_wait_time(t)
        alt_route_time = wait_time * 0.3
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
    
    def _reroute_vehicle(self, vid, decision):
        self.rerouted_vehicles[vid] = {
            'time': decision['time'],
            'time_saved': decision['time_saved']
        }
        
        Logger.log(f"Vehicle {vid} rerouted (saved {decision['time_saved']:.0f}s)")
    
    def get_stats(self):
        if not self.reroute_decisions:
            return {}
        
        rerouted = [d for d in self.reroute_decisions if d['should_reroute']]
        
        return {
            'total_decisions': len(self.reroute_decisions),
            'rerouted': len(rerouted),
            'total_time_saved': sum(d['time_saved'] for d in rerouted)
        }